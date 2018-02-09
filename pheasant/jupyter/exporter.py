from typing import Callable

import nbformat
from nbconvert import MarkdownExporter
from traitlets.config import Config

from .cache import abort, memoize
from .client import run_cell
from .config import config


def new_exporter(loader=None, template_file=None):
    c = Config({'NbConvertBase': {
        'display_data_priority': ['application/vnd.jupyter.widget-state+json',
                                  'application/vnd.jupyter.widget-view+json',
                                  'application/javascript',
                                  'text/html',
                                  'text/markdown',
                                  'image/svg+xml',
                                  'text/latex',
                                  'image/png',
                                  'image/jpeg',
                                  'text/plain']
    }})

    exporter = MarkdownExporter(config=c,
                                extra_loaders=[loader] if loader else None)
    exporter.template_file = template_file
    return exporter


def export(cell) -> str:
    """Convert a cell into markdown with `template`."""
    notebook = nbformat.v4.new_notebook(cells=[cell], metadata={})
    markdown = config['exporter'].from_notebook_node(notebook)[0]
    return markdown


def inline_export(cell, escape=False) -> str:
    """Convert a cell into markdown with `inline_template`."""
    notebook = nbformat.v4.new_notebook(cells=[cell], metadata={})
    markdown = config['inline_exporter'].from_notebook_node(notebook)[0]

    if escape:
        # FIXME
        markdown = f'{markdown}'
    elif markdown.startswith("'") and markdown.endswith("'"):
        markdown = str(eval(markdown))

    return markdown


def inspect_export(cell) -> str:
    """Convert a cell generated by inspection into markdown."""
    for output in cell['outputs']:
        if 'data' in output and 'text/plain' in output['data']:
            lines, lineno = eval(output['data']['text/plain'])
            return ''.join(lines)
            break
    else:
        return ''


@abort
@memoize
def run_and_export(cell, export: Callable[..., str], kernel_name=None) -> str:
    """Run a code cell and export the source and outputs into markdown.

    These two functions are defined in this function in order to cache the
    source and outputs to avoid rerunning the cell unnecessarily.
    """
    run_cell(cell, kernel_name)
    return export(cell)