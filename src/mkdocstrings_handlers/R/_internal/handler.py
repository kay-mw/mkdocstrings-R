from typing import ClassVar

from mkdocstrings import BaseHandler, get_logger

logger = get_logger(__name__)


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

    def collect(self, identifier, options):
        logger.info(identifier)
        logger.info(options)
        return {"a": 1}

    def render(self, data, options, locale=None) -> str:
        logger.info(data)
        logger.info(options)
        logger.info(locale)

        return "{'a': 1}"

    def get_options(self, local_options):
        return local_options


def get_handler(**kwargs):
    return RHandler(**kwargs)
