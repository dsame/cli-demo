import os
import platform

from distutils.dir_util import copy_tree
from git import IndexFile, Repo
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from shutil import copytree, ignore_patterns, rmtree

from oml.exceptions import OMLException
from oml.settings import (MODEL_META_FILENAME, PYTHON_LANG, CSHARP_LANG, TEMPLATE_ADDONS_DIR_PATH,
    TEMPLATE_COMMON_DIR_PATH, TEMPLATE_LANG_DIR_PATH, update_model_metadata, load_model_metadata)
from oml.util.shell import exec_dotnet, exec_nuget
from oml.util.os import get_user


class TemplateFactory:

    def __init__(self, language, template='base'):
        self.language = language
        self.template = template if template is not None else 'base'
        self.base_template_dirpath = os.path.join(TEMPLATE_LANG_DIR_PATH,
            self.language, 'base')
        self.custom_template_dirpath = os.path.join(TEMPLATE_LANG_DIR_PATH,
            self.language, self.template)

        if not os.path.exists(self.base_template_dirpath) or not os.path.exists(self.custom_template_dirpath):
            raise OMLException('Template not found.')

    def generate(self, path, flavor=None, build_mode=None, serve_platform=None):
        # Generate project's metadata
        model_name = self._get_model_name(path)

        # Generate a project based on base + custom template
        if self.language == PYTHON_LANG:
            self._generate_python_code(path, model_name, flavor, serve_platform)
        elif self.language == CSHARP_LANG:
            if platform.system() == 'Windows':
                self._generate_csharp_code(path, model_name)
                serve_platform = 'dlisv3binary'
            else:
                raise OMLException('C# template only supported in Windows platform.')

        # Generate common files
        self._generate_common_files(path, flavor, model_name, serve_platform)
        print('Created new project: {}'.format(model_name))

        # Add build mode to metadata
        if self.language == CSHARP_LANG:
            metadata = load_model_metadata(path)
            metadata['buildmode'] = build_mode
            update_model_metadata(path, metadata)

    def generate_multistage_pipeline_template(self, path, model_name):
        rootdir = self._git_rel_path(path) or model_name
        pipelines_dirpath = os.path.join(path, '.azure-pipelines')
        azure_templates_dirpath = os.path.join(self.base_template_dirpath, '.azure-pipelines')
        if Path(os.path.join(pipelines_dirpath, 'multistage-pipeline.yml')).exists():
            print("Multistage pipeline template already exists.")
        else:
            env = Environment(loader=FileSystemLoader(azure_templates_dirpath), autoescape=True)
            template = 'tpl_multistage-pipeline.yml'
            if Path(os.path.join(azure_templates_dirpath, template)).exists():
                dest = os.path.join(pipelines_dirpath, 'multistage-pipeline.yml')
                env.get_template(template).stream(
                    namespace=model_name,
                    rootdir=rootdir).dump(dest)
                print('Generated new multistage pipeline template in .azure-pipelines directory')

    def generate_noncomp_pipeline_template(self, path, model_name):
        rootdir = self._git_rel_path(path) or model_name
        pipelines_dirpath = os.path.join(path, '.azure-pipelines')
        if Path(os.path.join(pipelines_dirpath, 'noncomp-pipeline.yml')).exists():
            print("Non-compliant pipeline template already exists.")
        else:
            env = Environment(loader=FileSystemLoader(TEMPLATE_ADDONS_DIR_PATH), autoescape=True)
            template = 'tpl_noncomp-pipeline.yml'
            if Path(os.path.join(TEMPLATE_ADDONS_DIR_PATH, template)).exists():
                dest = os.path.join(pipelines_dirpath, 'noncomp-pipeline.yml')
                env.get_template(template).stream(
                    namespace=model_name,
                    language=self.language,
                    rootdir=rootdir).dump(dest)
                print('Generated new non-compliant pipeline template in .azure-pipelines directory')

    def _generate_csharp_code(self, dest, model_name):
        # Register the template
        exec_dotnet(['new', '-i', self.custom_template_dirpath])

        # Create the new project using the specified template
        exec_dotnet(['new', '{}model'.format(self.template),
            '-n', model_name, '-o', dest, '--force'])

        # Restore project
        exec_nuget(['restore', os.path.join(dest, '{}.sln'.format(model_name)),
            '-ConfigFile', os.path.join(dest, 'nuget.config')])

        # Copy azure-pipelines folder
        pipeline_dirname = '.azure-pipelines'
        src = os.path.join(self.base_template_dirpath, pipeline_dirname)
        copytree(src, os.path.join(dest, pipeline_dirname), ignore=ignore_patterns('tpl_*'))

        # Generate template
        rootdir = self._git_rel_path(dest) or model_name
        self._generate_templated_files(dest, model_name, rootdir)

    def _generate_python_code(self, dest, model_name, flavor, serve_platform):
        # Truncate existing folder
        if os.path.exists(dest):
            rmtree(dest)
        copytree(self.base_template_dirpath, dest, ignore=ignore_patterns('tpl_*'))
        if self.template != 'base':
            copy_tree(self.custom_template_dirpath, dest)

        # Generate template
        rootdir = self._git_rel_path(dest) or model_name
        self._generate_templated_files(dest, model_name, rootdir, serve_platform, flavor)

        # Rename package folder name
        os.rename(os.path.join(dest, 'code'), os.path.join(dest, model_name))

    def _generate_common_files(self, path, flavor, model_name, serve_platform):
        env = Environment(loader=FileSystemLoader(TEMPLATE_COMMON_DIR_PATH), autoescape=True)
        template = env.get_template(MODEL_META_FILENAME)
        template.stream(
            name=model_name,
            version='1.0.0',
            owner=get_user(),
            language=self.language,
            flavor=flavor if flavor is not None else 'null',
            flavor_version='latest' if flavor is not None else 'null',
            input_schema='null',
            output_schema='null',
            platform=serve_platform or 'null'
        ).dump(os.path.join(path, MODEL_META_FILENAME))

        readme = 'README.md'
        template = env.get_template(readme)
        template.stream(namespace=model_name).dump(os.path.join(path, readme))

    def _get_model_name(self, path, model_name=None):
        if model_name is None:
            model_name = os.path.basename(path)
        return model_name

    def _generate_templated_files(self, dest, model_name, rootdir, serve_platform='', flavor=''):
        env = Environment(
            loader=FileSystemLoader(self.base_template_dirpath),
            autoescape=True,
            keep_trailing_newline=True
        )
        for root, dirs, files in os.walk(self.base_template_dirpath):
            for fn in files:
                prefix = 'tpl_'
                suffix = 'pyc'
                if fn.startswith(prefix) and not fn.endswith(suffix):
                    basename = os.path.basename(root.replace(self.base_template_dirpath, ''))
                    tpl_name = '/'.join([basename, fn])
                    fpath = os.path.join(dest, basename, fn.replace(prefix, ''))
                    env.get_template(tpl_name).stream(
                        namespace=model_name,
                        flavor=flavor,
                        platform=serve_platform,
                        rootdir=rootdir).dump(fpath)

    @staticmethod
    def _git_rel_path(path):
        try:
            repo = Repo(path, search_parent_directories=True)
            index = IndexFile(repo)
            path = Path(index._to_relative_path(path))
            return path.as_posix()
        except Exception:
            return ''
