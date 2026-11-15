import ast
import os
import unittest

import demo_shop_core_lib
from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop

LIBRARY_DIR = os.path.dirname(os.path.abspath(demo_shop_core_lib.__file__))
# entities and migrations DECLARE the column names; everything else reads Entity.column.key
DECLARING_DIRS = (
    os.path.join(LIBRARY_DIR, 'data_layers', 'data', 'db', 'entities'),
    os.path.join(LIBRARY_DIR, 'data_layers', 'data', 'db', 'migrations'),
)
COLUMN_NAMES = {column.key for column in DemoShop.__table__.columns}


def _offenders(source: str, file_name: str) -> list:
    return [
        '{}:{} {!r}'.format(file_name, node.lineno, node.value)
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in COLUMN_NAMES
    ]


def _python_files():
    for directory, _, file_names in os.walk(LIBRARY_DIR):
        if directory.startswith(DECLARING_DIRS):
            continue
        for file_name in file_names:
            if file_name.endswith('.py'):
                yield os.path.join(directory, file_name)


class TestColumnNameLiterals(unittest.TestCase):

    def test_no_column_name_is_written_as_a_string_literal(self):
        offenders = []
        files = list(_python_files())
        self.assertGreaterEqual(len(files), 4)  # the walk really found the library sources
        for path in files:
            with open(path, encoding='utf-8') as file:
                offenders.extend(_offenders(file.read(), os.path.relpath(path, LIBRARY_DIR)))
        self.assertEqual([], offenders)

    def test_the_walk_catches_a_planted_literal(self):
        planted = 'payload = {{{!r}: 1}}\n'.format(sorted(COLUMN_NAMES)[0])
        self.assertEqual(1, len(_offenders(planted, 'planted.py')))
