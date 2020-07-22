import os
import shutil
import sys
import platform

from bottle import post, request, response, run
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader
from importlib.util import spec_from_file_location, module_from_spec
from shutil import copytree, ignore_patterns

from oml.exceptions import OMLException
from oml.models import BaseModel
from oml.settings import MODEL_FILENAME, TEMPLATE_PLATFORM_DIR_PATH, PYTHON_LANG
from oml.util.shell import run_shell
from oml.util.zip import archive
from oml.util.manifest import create_manifest


class PythonModel(BaseModel):

    def __init__(
            self,
            model_name,
            model_version,
            base_path,
            tmp_dir_path,
            package_dir_path,
            proj_dir_path):
        self.model_name = model_name
        self.model_version = model_version
        self.base_path = base_path
        self.package_dir_path = package_dir_path
        self.proj_dir_path = proj_dir_path
        self.data_dir_path = os.path.join(self.base_path, 'data')
        self.model_package_dir_path = os.path.join(self.package_dir_path, 'model')
        self.conda_package_path = os.path.join(tmp_dir_path, 'env', self.model_name)

    def eval(self):
        model = self._load_model()
        model.eval()

    def serve(self, port):
        model = self._load_model()

        def handler():
            data = request.body.read().decode('utf-8')
            response.content_type = 'text/plain'
            return model.predict(data)

        print("""To use the server, run the following command from another shell:
            curl http://localhost:{} --data \"test input here\"""".format(port))
        post('/')(handler)
        run(host='localhost', port=port)

    def test(self):
        os.chdir(self.base_path)
        try:
            run_shell(['test.cmd'])
        except Exception:
            raise OMLException('test.cmd file not found.')

    def package(self, platform, skip_archive):
        if (platform == 'dlis') or (platform == 'qas'):
            self._package_platform(platform, skip_archive)
            print('Packaged the model with ' + platform + ' template.')

    def copy_metadata(self, model_meta_filename):
        # Copy oml metadata into the package folder
        src = os.path.join(self.base_path, model_meta_filename)
        dst = os.path.join(self.model_package_dir_path, model_meta_filename)
        shutil.copyfile(src, dst)

    def create_manifests(self):
        if not os.path.exists(self.model_package_dir_path) or not os.path.exists(self.conda_package_path):
            raise FileExistsError('Package folder not found. Please run "oml package" before generating manifests.')

        # create model manifest
        create_manifest(self.model_package_dir_path)
        print('Created SecureManifest.json in {}'.format(self.model_package_dir_path))
        # create conda manifest
        create_manifest(self.conda_package_path)
        print('Created SecureManifest.json in {}'.format(self.conda_package_path))

    def check_manifest_exists(self):
        model_manifest_path = os.path.join(self.model_package_dir_path, 'SecureManifest.json')
        return os.path.exists(model_manifest_path)

    def _load_model(self):
        sys.path.append(self.base_path)
        path = os.path.join(self.proj_dir_path, MODEL_FILENAME)
        spec = spec_from_file_location('{}.model'.format(self.model_name), path)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.Model(self.data_dir_path)

    def _package_platform(self, platform_name, skip_archive):
        if platform.system() != 'Windows':
            raise OMLException('OS is not supported: {}'.format(platform.system()))

        # Copy static files
        template_dir_path = os.path.join(TEMPLATE_PLATFORM_DIR_PATH, platform_name, PYTHON_LANG)
        copytree(template_dir_path, self.model_package_dir_path, ignore=ignore_patterns('tpl_*'))
        copy_tree(self.data_dir_path, os.path.join(self.model_package_dir_path, 'data'))

        # Generate code based on template
        env = Environment(loader=FileSystemLoader(template_dir_path), autoescape=True)
        for root, dirs, files in os.walk(template_dir_path):
            for fn in files:
                prefix = 'tpl_'
                suffix = 'pyc'
                if fn.startswith(prefix) and not fn.endswith(suffix):
                    basename = os.path.basename(root.replace(template_dir_path, ''))
                    tpl_name = '/'.join([basename, fn])
                    fpath = os.path.join(self.model_package_dir_path, basename, fn.replace(prefix, ''))
                    env.get_template(tpl_name).stream(
                        namespace=self.model_name,
                        version=self.model_version).dump(fpath)

        # Package Conda environment
        self._package_conda(skip_archive)

    def _package_conda(self, skip_archive):
        os.chdir(self.base_path)
        run_shell(['setup.cmd'])

        if not skip_archive:
            print('Zipping conda environment...')
            dest = os.path.join(self.package_dir_path, 'conda')
            os.makedirs(dest, exist_ok=True)
            archive(self.conda_package_path, dest, self.model_name)
