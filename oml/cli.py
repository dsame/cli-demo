import click
import os
import re

from prettytable import PrettyTable
from oml.context import pass_context
from oml.factory import TemplateFactory
from oml.hooks.gitrepo import GitRepositoryHook
from oml.model import Model
from oml.settings import PYTHON_LANG, CSHARP_LANG

import oml.platforms.dlis.cli as dlis
import oml.platforms.azureml.cli as azureml


@click.group(context_settings=dict(
    auto_envvar_prefix='OML',
    help_option_names=['-h', '--help'],
    ignore_unknown_options=True,
    max_content_width=100
))
@click.version_option()
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode.')
@pass_context
def main(ctx, verbose):
    """Machine Learning Model Management Tool"""
    ctx.verbose = verbose
    # ctx.is_outdated()


@main.command()
@click.argument('model-name', required=False)
@pass_context
def list(ctx, model_name):
    """Lists all published versions of a model."""
    try:
        ctx.tracker.track_event('command', 'list')
        model = Model(os.getcwd(), ctx.verbose)
        result = model.list_artifacts(model_name)
        if result:
            tbl = PrettyTable(['Version', 'Path', 'Platform',
                'Compliant', 'Created'], align='l')
            for row in result:
                tbl.add_row([
                    row['version'],
                    row['path'],
                    row['platform'].upper(),
                    'False' if row['is_compliant'] == 0 else 'True',
                    row['created_at']])
            ctx.log(tbl)
            ctx.log('{} published version(s) found.'.format(len(result)))
        else:
            ctx.log("The model doesn't have any published versions.")
    except Exception as e:
        ctx.tracker.track_event('exception', 'list')
        ctx.error_log(e)


# @main.command()
@click.argument('path', required=False, type=click.Path(resolve_path=True))
@pass_context
def push(ctx, path):
    """Push a model into OXO model repository."""
    try:
        model = Model(os.getcwd(), ctx.verbose)
        if path is None:
            path = model.base_path
        repo = GitRepositoryHook()
        repo.push_model(path)
    except Exception as e:
        ctx.error_log(e)


# @main.command()
@pass_context
def pull(ctx):
    """Clone OXO model repository."""
    try:
        repo = GitRepositoryHook()
        repo.pull_model()
    except Exception as e:
        ctx.error_log(e)


def validate_name(ctx, param, value):
    name = os.path.basename(value)
    charRe = re.compile(r'[^a-zA-Z0-9.]')
    symbol_found = bool(charRe.search(name))
    if symbol_found:
        raise click.BadParameter(' name can contain only letters and digits')
    return(value)


@main.command()
@click.argument('name', callback=validate_name, type=click.Path(resolve_path=True))
@click.option('-f', '--flavor',
    type=click.Choice(['tensorflow', 'scikit-learn', 'pytorch', 'lightgbm']),
    help='Flavor of machine learning framework.')
@click.option('-t', '--template',
    type=click.Choice(['nlx', 'tellme']),
    help='Template to initialize a new project.')
@click.option('-l', '--language', default=PYTHON_LANG, show_default=True,
    type=click.Choice([PYTHON_LANG, CSHARP_LANG]),
    help='Code language for the template.')
@click.option('-b', '--build-mode', default='Release', show_default=True,
    type=click.Choice(['Release', 'Debug']),
    help='Build mode for c# projects.')
@click.option('-p', '--platform', default='dlis', show_default=True,
    type=click.Choice(['dlis', 'qas']),
    help='platform to initialize a new project.')
@pass_context
def init(ctx, name, flavor, template, language, build_mode, platform):
    """Create a new project from a template."""
    try:
        ctx.tracker.track_event('command', 'init')
        factory = TemplateFactory(language, template)
        factory.generate(name, flavor, build_mode, platform)
    except Exception as e:
        ctx.tracker.track_event('exception', 'init')
        ctx.error_log(e)


@main.command()
@click.option('--port', default=8000, show_default=True,
    help='Port number that is serving the service.')
@pass_context
def serve(ctx, port):
    """Serving current model at localhost."""
    try:
        ctx.tracker.track_event('command', 'serve')
        model = Model(os.getcwd(), ctx.verbose)
        model.serve(port)
    except Exception as e:
        ctx.tracker.track_event('exception', 'serve')
        ctx.error_log(e)


@main.command()
@pass_context
def eval(ctx):
    """Batch scoring on current model."""
    try:
        ctx.tracker.track_event('command', 'eval')
        model = Model(os.getcwd(), ctx.verbose)
        model.eval()
    except Exception as e:
        ctx.tracker.track_event('exception', 'eval')
        ctx.error_log(e)


@main.command()
@click.option('-f', '--file-path', type=click.Path(resolve_path=True),
    help='File contains request and expected queries. File path is required when mode = live.')
@click.option('-d', '--delimiter', default='\t', show_default=True,
    help='Unit test file delimiter.')
@click.option('-m', '--mode', default='offline', show_default=True,
    type=click.Choice(['live', 'offline']),
    help='Testing mode.')
@click.option('-e', '--endpoint', default='http://localhost:8000', show_default=True,
    help='The endpoint that is serving a model.')
@pass_context
def test(ctx, file_path, delimiter, mode, endpoint):
    """Running unit tests on current model."""
    try:
        ctx.tracker.track_event('command', 'test')
        model = Model(os.getcwd(), ctx.verbose)
        model.test(mode, file_path, delimiter, endpoint, ctx.verbose)
    except Exception as e:
        ctx.tracker.track_event('exception', 'test')
        ctx.error_log(e)


@main.command()
@click.option('-p', '--platform', default=None, show_default=True, hidden=True,
    type=click.Choice(['dlis', 'dlisv3', 'dlisv3binary', 'qas']),
    help='Serving platform to serve a model. Choose dlisv3 (or dlisv3binary) to use IDLWindowsModelV3 for c# models.')
@click.option('--skip-archive', is_flag=True, default=False, hidden=True,
    help='Whether to skip archive when packaging.')
@pass_context
def package(ctx, platform, skip_archive):
    """Package the model."""
    try:
        ctx.tracker.track_event('command', 'package')
        model = Model(os.getcwd(), ctx.verbose)
        if model.language == 'python' and (platform == 'dlisv3' or platform == 'dlisv3binary'):
            ctx.log('Warning: Packaging with dlisv3 is only supported for c# models, continue packaging with dlis.')
            platform = 'dlis'
        model.package(platform, skip_archive)
    except Exception as e:
        ctx.tracker.track_event('exception', 'package')
        ctx.error_log(e)


@main.command()
@click.option('-s', '--storage', default=None, hidden=True,
    type=click.Choice(['cosmos', 'adls']),
    help='File system storage name.')
@click.option('-V', '--version', help='Custom version number.')
@click.option('--increment-type', default='patch', show_default=True,
    type=click.Choice(['major', 'minor', 'patch']),
    help='Version increment part.')
@click.option('-d', '--datasource-id', help="""When using an Aether-trained model,
    provide the datasource id for the model. ADLS only. """)
@click.option('--is-compliant/--non-compliant', is_flag=True, default=None, hidden=True,
    help='Whether to force the publish to act as non-compliant. For use in non-compliant Azure pipelines.')
@pass_context
def publish(ctx, storage, version, increment_type, datasource_id, is_compliant):
    """Publish model into storage."""
    try:
        ctx.tracker.track_event('command', 'publish')
        model = Model(os.getcwd(), ctx.verbose)
        model.publish(storage, datasource_id, version, increment_type, is_compliant)
    except Exception as e:
        ctx.tracker.track_event('exception', 'publish')
        ctx.error_log(e)


@main.command()
@pass_context
def generate_multistage_template(ctx):
    """Generate multistage pipelines template for an existing project."""
    try:
        ctx.tracker.track_event('command', 'generate_multistage_template')
        model = Model(os.getcwd(), ctx.verbose)
        factory = TemplateFactory(model.language)
        factory.generate_multistage_pipeline_template(model.base_path, model.model_name)
    except Exception as e:
        ctx.tracker.track_event('exception', 'generate_multistage_template')
        ctx.error_log(e)


@main.command()
@pass_context
def generate_noncomp_template(ctx):
    """Generate non-compliant pipeline template."""
    try:
        ctx.tracker.track_event('command', 'generate_noncomp_template')
        model = Model(os.getcwd(), ctx.verbose)
        factory = TemplateFactory(model.language)
        factory.generate_noncomp_pipeline_template(model.base_path, model.model_name)
    except Exception as e:
        ctx.tracker.track_event('exception', 'generate_noncomp_template')
        ctx.error_log(e)


main.add_command(dlis.commands)
main.add_command(azureml.commands)
