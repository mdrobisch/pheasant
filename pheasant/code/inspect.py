import os
import re
from typing import Generator

from pheasant.code.config import config
from pheasant.jupyter.renderer import execute_and_render
from pheasant.markdown.splitter import escaped_splitter_join
from pheasant.number import config as config_number
from pheasant.utils import read_source


def convert(source: str) -> str:
    source = ''.join(render(source))
    return source


def render(source: str) -> Generator[str, None, None]:
    pattern_escape = r'(```(.*?)```)|(~~~(.*?)~~~)'
    pattern_code = config['code_pattern']

    splitter = escaped_splitter_join(pattern_code, pattern_escape, source)
    for splitted in splitter:
        if isinstance(splitted, str):
            yield splitted
        else:
            language, reference = splitted.group(1, 2)
            if splitted.group().startswith('#'):
                yield generate_header(language, reference)

            if language == 'python':
                yield inspect(reference)
            elif language == 'file':
                yield read_file(reference)
            elif language.startswith('#'):
                yield splitted.group().replace('#', '')
            else:
                yield splitted.group()


def generate_header(language: str, reference: str) -> str:
    if language == 'python':
        name = 'Code'
    elif language == 'file':
        name = 'File'
    else:
        return ''
    return f'#{name} {reference}\n'


def inspect(symbol: str) -> str:
    """Inspect source code."""
    def render(context: dict) -> str:
        """Convert an output generated by inspection into markdown."""
        for output in context['outputs']:
            if 'data' in output and 'text/plain' in output['data']:
                lines, lineno = eval(output['data']['text/plain'])
                source = ''.join(lines)
                return fenced_code(source, 'python')
        return ''

    code = f'inspect.getsourcelines({symbol})'
    return execute_and_render(code, render, language='python')


def read_file(path: str) -> str:
    """Read a file from disc.

    `path`: `[path_to_file]<slice>?[language]` form is avaiable.
    Otherwise, the language is determined from the path's extension.
    For example, If the path is `a.py`, then the language is Python.

    """
    if '?' in path:
        path, language = path.split('?')
    else:
        language = ''

    match = re.match(r'(.+)<(.+?)>', path)

    if match:
        path, slice_str = match.groups()
    else:
        slice_str = ''

    if path.startswith('~'):
        path = os.path.expanduser(path)

    if not os.path.exists(path):
        return f'<p style="font-color:red">File not found: {path}</p>'

    if not language:
        ext = os.path.splitext(path)[-1]
        if ext:
            ext = ext[1:]  # Remove a dot.
        for language in config['language']:
            if ext in config['language'][language]:
                break
        else:
            language = ''

    source = read_source(path)

    if slice_str:
        sources = source.split('\n')
        if ':' not in slice_str:
            source = sources[int(slice_str)]
        else:
            slice_list = [int(s) if s else None for s in slice_str.split(':')]
            source = '\n'.join(sources[slice(*slice_list)])

    return fenced_code(source, language)


def fenced_code(source: str, language: str = '') -> str:
    begin = config_number['begin_pattern']
    end = config_number['end_pattern']
    cls = '.pheasant-fenced-code .pheasant-code'

    if not source.endswith('\n'):
        source = source + '\n'

    return f'{begin}\n~~~{language} {cls}\n{source}~~~\n{end}\n'
