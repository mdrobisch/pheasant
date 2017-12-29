import logging

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

from ..converters import convert, get_converter_name, get_converters

logger = logging.getLogger('mkdocs')

DEFAULT_SCHEMA = tuple([(get_converter_name(converter),
                         config_options.Type(dict, default={'enabled': False}))
                        for converter in get_converters()])


class PheasantPlugin(BasePlugin):
    config_scheme = DEFAULT_SCHEMA

    def on_page_read_source(self, source, page, config):
        """
        The on_page_read_source event can replace the default mechanism
        to read the contents of a page's source from the filesystem.

        Parameters
        ----------
        source: None
        page: mkdocs.nav.Page instance
        config: global configuration object

        Returns
        -------
        The raw source for a page as unicode string. If None is returned, the
        default loading from a file will be performed.
        """
        logger.info(f'[pheasant] Converting: {page.abs_input_path}')
        return convert(page.abs_input_path,
                       config['plugins']['pheasant'].config)