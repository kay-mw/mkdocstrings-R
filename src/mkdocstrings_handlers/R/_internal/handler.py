import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Mapping

from mkdocs.exceptions import PluginError
from mkdocstrings import (
    BaseHandler,
    CollectionError,
    CollectorItem,
    HandlerOptions,
    get_logger,
)


@contextmanager
def suppress_output():
    old_stdout_fd = os.dup(1)
    old_stderr_fd = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        os.close(devnull)
        yield
    finally:
        os.dup2(old_stdout_fd, 1)
        os.dup2(old_stderr_fd, 2)
        os.close(old_stdout_fd)
        os.close(old_stderr_fd)


# This import can produce a significant amount of R output, which looks very out of
# place next to proper mkdocs logging. This redirects all R output to DEVNULL for the
# duration of this import.
with suppress_output():
    from rpy2.robjects.packages import importr

logger = get_logger(__name__)


@dataclass
class Param:
    name: str
    description: str


@dataclass
class Docstring:
    name: str
    source: str
    signature: str
    title: str | None
    description: str | None
    details: str | None
    params: list[Param]
    returns: str | None
    examples: list | None


@dataclass
class Data:
    docstrings: list[Docstring]
    html_id: str


class RHandler(BaseHandler):
    name: ClassVar[str] = "R"
    """The handler's name."""

    domain: ClassVar[str] = "R"
    """The handler's domain, used to register objects in the inventory."""

    enable_inventory: ClassVar[bool] = False
    """Whether the inventory creation is enabled."""

    fallback_theme: ClassVar[str] = "material"
    """Fallback theme to use when a template isn't found in the configured theme."""

    extra_css: str = ""
    """Extra CSS."""

    def __init__(self, handler_config: dict | None, tool_config: Any, **kwargs):
        super().__init__(**kwargs)

        self.lib_loc = None
        """
        The path/location of the R library. This library must contain roxygen2.
        
        `lib_loc` only needs to be set if ryp2 can't auto-detect your `lib_loc`. For
        example, if your `renv/` folder isn't in the directory where you're running
        mkdocs.

        If you're unsure what your `lib_loc`(s) are, run `.libPaths()` in an R REPL.
        """
        if handler_config:
            self.lib_loc = handler_config.get("lib_loc")

    def collect(self, identifier: str, options: HandlerOptions) -> Data:
        file_path = Path(identifier.replace(".", "/"))
        file_path_ext = Path(f"{file_path}.R")
        if not file_path_ext.exists():
            raise CollectionError(
                f"Could not find {identifier} at path {str(file_path_ext)}"
            )

        roxygen2 = importr(
            "roxygen2",
            lib_loc=self.lib_loc,
        )
        results = roxygen2.parse_file(str(file_path_ext))
        docstrings: list[Docstring] = []
        for _, result in results.items():
            name = str(result.rx2("object").rx2("topic")[0])
            source = str(result.rx2("call"))

            call = re.match(r"function\([^{]*", source)
            if call:
                call = call.group(0).strip()
            else:
                raise PluginError(
                    f"Could not extract function signature for {identifier}"
                )
            signature = f"{name} <- {call}"

            tags = result.rx2("tags")
            title = None
            description = None
            details = None
            params: list[Param] = []
            returns = None
            examples = None
            for tag in tags:
                tag_name = str(tag.rx2("tag")[0])
                tag_val = str(tag.rx2("val")[0])
                if tag_name.startswith("title"):
                    title = tag_val
                elif tag_name.startswith("description"):
                    description = tag_val
                elif tag_name.startswith("details"):
                    details = tag_val
                elif tag_name.startswith("param"):
                    param_name = tag.rx2("val").rx2("name")[0]
                    param_description = tag.rx2("val").rx2("description")[0]
                    param = Param(name=param_name, description=param_description)
                    params.append(param)
                elif tag_name.startswith("return"):
                    returns = tag_val
                elif tag_name.startswith("examples"):
                    examples = tag_val.splitlines()

            docstring = Docstring(
                name=name,
                source=source,
                signature=signature,
                title=title,
                description=description,
                details=details,
                params=params,
                returns=returns,
                examples=examples,
            )
            docstrings.append(docstring)

        data = Data(docstrings=docstrings, html_id=str(file_path_ext))

        return data

    def render(
        self, data: CollectorItem, options: HandlerOptions, locale: str | None = None
    ) -> str:
        template = self.env.get_template("function.html.jinja")

        return template.render(
            options=options,
            data=data,
        )

    def get_options(self, local_options: Mapping[str, Any]):
        return local_options


def get_handler(handler_config: dict | None, tool_config: Any, **kwargs):
    return RHandler(handler_config=handler_config, tool_config=tool_config, **kwargs)
