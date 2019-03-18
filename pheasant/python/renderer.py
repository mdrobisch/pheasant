from typing import Iterator

from pheasant.core.renderer import Renderer
from pheasant.python.formatter import Formatter
from pheasant.python.splitter import splitter


class Python(Renderer):

    PYTHON_CODE_PATTERN = r"^(?P<source>.+)"  # Entire source!

    def __post_init__(self):
        super().__post_init__()
        self.register(Python.PYTHON_CODE_PATTERN, self.render_python_code)

    def render_python_code(self, context, splitter_: Iterator) -> Iterator[str]:
        formatter = Formatter(context.group.source)
        for cell_type, begin, end in splitter(context.group.source):
            yield formatter(cell_type, begin, end)
