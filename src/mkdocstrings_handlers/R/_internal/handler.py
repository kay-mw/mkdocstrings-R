import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from mkdocstrings import BaseHandler, CollectionError, get_logger

logger = get_logger(__name__)


@dataclass
class Param:
    name: str
    description: str


@dataclass
class Docstring:
    name: str
    description: str
    params: list[Param]
    returns: str
    examples: str


@dataclass
class Data:
    docstring: Docstring
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

    def __init__(self, handler_config, tool_config, **kwargs):
        super().__init__(**kwargs)

    def collect(self, identifier: str, options) -> Data:
        """
        Some docstring.

        Parameters:
            identifier: The name of the person to greet.

        Returns:
            A greeting message.
        """
        logger.info(f"{identifier=}")
        logger.info(f"{options=}")

        # TODO: Detect OS and use backslashes for Windows.
        file_path = Path(identifier.replace(".", "/"))
        file_path_ext = Path(f"{file_path}.R")
        if not file_path_ext.exists():
            raise CollectionError(
                f"Could not find {identifier} at path {str(file_path_ext)}"
            )

        description = ""
        params = []
        returns = ""
        examples = ""
        with open(file_path_ext, "r") as file:
            contents = file.readlines()
            docstrings = ""
            for line in contents:
                if line.startswith("#'"):
                    if line.strip() == "#'":
                        continue

                    text = re.sub(r"#' ", "", line)
                    docstrings += text

            split_docs = docstrings.split("@")
            for doc in split_docs:
                if doc.startswith("param "):
                    param_components = re.split("(?=[A-Z])", doc, maxsplit=1)
                    param_name = param_components[0].replace("param ", "").strip()
                    param_description = param_components[1]
                    param = Param(name=param_name, description=param_description)
                    params.append(param)
                elif doc.startswith("returns "):
                    returns += doc.replace("returns ", "")
                elif doc.startswith("examples"):
                    examples += f"`{doc.replace('examples', '')}`"
                else:
                    description += doc

        docstring = Docstring(
            name=file_path.name,
            description=description,
            params=params,
            returns=returns,
            examples=examples,
        )
        data = Data(docstring=docstring, html_id=str(file_path))

        logger.info(data)

        return data

    def render(self, data, options, locale=None) -> str:
        logger.info(f"{data=}")
        template = self.env.get_template("test.html.jinja")

        return template.render(
            options=options,
            data=data,
        )

    def get_options(self, local_options):
        return local_options


def get_handler(handler_config, tool_config, **kwargs):
    return RHandler(handler_config=handler_config, tool_config=tool_config, **kwargs)
