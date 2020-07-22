import os
import sys
import tempfile

from oml.factory import TemplateFactory
from oml.settings import CSHARP_LANG, PYTHON_LANG
from unittest import skipUnless, TestCase


class TestTemplateFactory(TestCase):

    def setUp(self):
        self.tmp_dirpath = tempfile.mkdtemp()

    def checkDependencies(self, path, dependencies):
        with open(path) as f:
            if dependencies in f.read():
                return True
            return False

    def test_python_initialize_base(self):
        factory = TemplateFactory(PYTHON_LANG)
        factory.generate(self.tmp_dirpath, 'tensorflow')
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'oml.yml')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'README.md')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.gitignore')), True)
        self.assertEqual(self.checkDependencies(os.path.join(self.tmp_dirpath, 'env-prod.yml'), 'QASOML'), False)

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_csharp_initialize_base(self):
        factory = TemplateFactory(CSHARP_LANG)
        factory.generate(self.tmp_dirpath, 'tensorflow', 'Release')
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'oml.yml')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'README.md')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.gitignore')), True)

    def test_qas_python_initialize_base(self):
        factory = TemplateFactory(PYTHON_LANG)
        factory.generate(self.tmp_dirpath, 'pytorch', 'Release', 'qas')
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'README.md')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, '.gitignore')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'oml.yml')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'env-dev.yml')), True)
        self.assertEqual(os.path.exists(os.path.join(self.tmp_dirpath, 'env-prod.yml')), True)
        self.assertEqual(self.checkDependencies(os.path.join(self.tmp_dirpath, 'env-prod.yml'), 'QASOML'), True)
        self.assertEqual(self.checkDependencies(os.path.join(self.tmp_dirpath, 'env-prod.yml'), 'pythonnet'), True)
