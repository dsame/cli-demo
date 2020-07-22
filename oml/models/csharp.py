import os
import shutil

from bottle import post, request, response, run
from distutils.dir_util import copy_tree
from shutil import copyfile

from oml.models import BaseModel
from oml.settings import TEMPLATE_PLATFORM_DIR_PATH, SCORE_FILENAME, CSHARP_LANG
from oml.util.shell import exec_dotnet, exec_nuget, run_shell
from oml.util.manifest import create_manifest


class CSharpModel(BaseModel):

    def __init__(
            self,
            model_name,
            base_path,
            tmp_dir_path,
            inference_dir_path,
            package_dir_path,
            proj_dir_path,
            metadata):
        self.model_name = model_name
        self.base_path = base_path
        self.tmp_dir_path = tmp_dir_path
        self.inference_dir_path = inference_dir_path
        self.package_dir_path = package_dir_path
        self.proj_dir_path = proj_dir_path
        self.build_mode = metadata.get('buildmode', 'Release')

        self.proj_bin_path = os.path.join(proj_dir_path, 'bin', 'x64', self.build_mode)
        self.exe_path = os.path.join(self.proj_bin_path, '{}.exe'.format(model_name))
        self.csproj_path = os.path.join(proj_dir_path, '{}.csproj'.format(model_name))
        self.sln_path = os.path.join(base_path, '{}.sln'.format(model_name))

        self.inference_proj = '{}Inference'.format(model_name)
        self.inference_proj_dir_path = os.path.join(self.inference_dir_path, self.inference_proj)
        self.inference_sln_path = os.path.join(self.inference_dir_path,
            '{}.sln'.format(self.inference_proj))
        self.inference_csproj_path = os.path.join(self.inference_proj_dir_path,
            '{}.csproj'.format(self.inference_proj))

    def eval(self):
        self._build_project(self.sln_path)
        run_shell([self.exe_path, 'eval'])

        # Copy .score file into base path
        src = os.path.join(self.proj_bin_path, SCORE_FILENAME)
        dest = os.path.join(self.base_path, SCORE_FILENAME)
        copyfile(src, dest)

    def serve(self, port):
        def handler():
            data = request.body.read().decode('utf-8')
            response.content_type = 'text/plain'
            cmd = [self.exe_path, 'predict', data]
            res = run_shell(cmd, capture_output=True)
            return res.rstrip()

        self._build_project(self.sln_path)
        print("""To use the server, run the following command from another shell:
            curl http://localhost:{} --data \"test input here\"""".format(port))
        post('/')(handler)
        run(host='localhost', port=port)

    def test(self):
        self._build_project(self.sln_path)
        exec_dotnet(['test', '--', 'MSTest.DeploymentEnabled=false'])

    def package(self, platform, skip_archive):
        os.makedirs(self.package_dir_path, exist_ok=True)
        os.makedirs(self.inference_dir_path, exist_ok=True)

        template_path = os.path.join(TEMPLATE_PLATFORM_DIR_PATH, platform, CSHARP_LANG)

        # Register DLIS template
        exec_dotnet(['new', '-i', template_path])

        # Create inference project in temp dir
        exec_dotnet(['new', platform, '-n', self.model_name,
            '-o', self.inference_dir_path, '--force'])

        self._package_dlis()
        print('Packaged the model with {} template.'.format(platform))

    def copy_metadata(self, model_meta_filename):
        # Copy oml metadata into the package folder
        src = os.path.join(self.base_path, model_meta_filename)
        dst = os.path.join(self.package_dir_path, model_meta_filename)
        shutil.copyfile(src, dst)

    def create_manifests(self):
        if not os.path.exists(self.package_dir_path):
            raise FileExistsError('Package folder not found. Please run "oml package" before generating manifests.')

        # create model manifest
        create_manifest(self.package_dir_path)
        print('Created SecureManifest.json in {}'.format(self.package_dir_path))

    def check_manifest_exists(self):
        manifest_path = os.path.join(self.package_dir_path, 'SecureManifest.json')
        return os.path.exists(manifest_path)

    def _package_dlis(self):
        proj_data_dir = os.path.join(self.proj_dir_path, 'data')
        inference_nuget_config_path = os.path.join(self.inference_dir_path, 'nuget.config')
        build_dir_path = os.path.join(self.inference_proj_dir_path, 'bin', 'x64', self.build_mode, 'publish')

        # Publish dependency runtime
        exec_nuget(['restore', self.inference_sln_path,
            '-ConfigFile', inference_nuget_config_path])
        exec_dotnet(['publish', self.inference_sln_path,
            '--configfile', inference_nuget_config_path,
            '-c', self.build_mode, '--force', '-o', build_dir_path])

        # Copy runtime and static files
        copy_tree(proj_data_dir, os.path.join(self.package_dir_path, 'data'))
        self._copy_dlls(self.proj_bin_path, self.package_dir_path)
        self._copy_files(build_dir_path, self.package_dir_path)

    def _build_project(self, sln_path):
        exec_dotnet(['build', sln_path, '-c', self.build_mode, '--force'])

    def _copy_dlls(self, src, dest):
        for root, dirs, files in os.walk(src):
            for f in files:
                runtime = os.path.join(dest, f)
                if not os.path.exists(runtime) and f.endswith('.dll'):
                    copyfile(os.path.join(root, f), runtime)

    def _copy_files(self, src, dest):
        for obj in os.listdir(src):
            srcpath = os.path.join(src, obj)
            destpath = os.path.join(dest, obj)
            if os.path.isfile(srcpath) and not os.path.exists(destpath):
                copyfile(srcpath, destpath)
