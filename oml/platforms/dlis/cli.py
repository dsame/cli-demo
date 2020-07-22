import click
import json
import os

from oml.context import pass_context
from oml.model import Model
from oml.platforms.dlis import DlisApi
from oml.settings import TEST_JOB_TYPE, DEPLOYMENT_JOB_TYPE
from prettytable import PrettyTable


@click.group('dlis')
def commands():
    """DLIS operation commands."""
    pass


@commands.command()
@click.option('-r', '--resource', default=TEST_JOB_TYPE, show_default=True,
    type=click.Choice([TEST_JOB_TYPE, DEPLOYMENT_JOB_TYPE]),
    help='Resource endpoint.')
@click.option('--id', help='Resource GUID.')
@pass_context
def show(ctx, resource, id):
    """Show detailed configurations on a given ID."""
    try:
        ctx.tracker.track_event('command', 'dlis_show')
        client = DlisApi()
        result = client.get(resource, id)
        if result is not None:
            ctx.log(json.dumps(result, indent=2))
        else:
            ctx.log('Not found. Please check that you specified the right resource type.')
    except Exception as e:
        ctx.tracker.track_event('exception', 'dlis_show')
        ctx.error_log(e)


@commands.command()
@click.option('-r', '--resource', default=TEST_JOB_TYPE, show_default=True,
    type=click.Choice([TEST_JOB_TYPE, DEPLOYMENT_JOB_TYPE]),
    help='Resource endpoint.')
@click.option('-n', '--model-name', help='Model name.')
@click.option('-o', '--owner', help='Model owner name.')
@click.option('-s', '--status', help='Task status.')
@pass_context
def list(ctx, resource, model_name, owner, status):
    """List user tests or deployments."""
    try:
        ctx.tracker.track_event('command', 'dlis_list')
        client = DlisApi()
        result = client.list(resource, model_name, owner, status)

        if result:
            tbl = PrettyTable([
                'ID', 'Model Name', 'Start Time',
                'End Time', 'Status', 'Namespace', 'Is Compliant', 'Error'], align='l')
            for row in result:
                tbl.add_row([
                    row['id'],
                    row['model_name'],
                    row['start_time'],
                    row['end_time'],
                    row['status'],
                    row['namespace'],
                    row['is_compliant'],
                    row['error']])
            ctx.log(tbl)
            ctx.log('{} {}(s) found.'.format(len(result), resource))
        else:
            ctx.log('No {}s found.'.format(resource))
    except Exception as e:
        ctx.tracker.track_event('exception', 'dlis_list')
        ctx.error_log(e)


@commands.command()
@click.option('-n', '--model-name', help='Model name.')
@click.option('--model-version', help='Model version. Using latest version if not set.')
@click.option('--model-type', type=click.Choice(['WindowsLibrary', 'WindowsProcess']),
    help='For Python, use WindowsProcess. For C#, use WindowsLibrary')
@click.option('--artifact-uri', help='Model package file location.')
@click.option('--test-query-uri', help='Test query set file path. Default: data/input.txt')
@click.option('--platform-type', default='Windows', show_default=True,
    type=click.Choice(['Windows']), help='Operating system type.')
@click.option('--timeout-in-ms', help='Per-query timeout on the model. Can be set in oml.yml. Default: 100')
@click.option('--max-query-size-in-bytes', help='Maximum query size in bytes. Can be set in oml.yml. Default: 65536')
@click.option('--qps',
    help='Queries per second to run. Can be set in oml.yml. Default: -1, computes the maximum QPS.')
@click.option('--waiting-model-ready-in-min',
    help='Model loading timeout in minute. Can be set in oml.yml. Default: 10')
@click.option('--cpu-cores', help='Number of CPU cores per instance. Can be set in oml.yml. Default: 2')
@click.option('--memory-usage-in-mb', help='Reserved memory per instance in MB. Can be set in oml.yml. Default: 2048')
@click.option('--gpu-devices', help='Number of GPU devices per instance. Can be set in oml.yml. Default: 0')
@click.option('--fpga-devices', help='Number of FGPA devices per instance. Can be set in oml.yml. Default: 0')
@click.option('--use-avx2/--no-use-avx2', is_flag=True, default=None,
    help='Whether to use AVX2. Can be set in oml.yml. Default: False')
@click.option('--env-vars',
    help='Environment variables to use, separated with semicolon in NAME=value format. Can be set in oml.yml')
@pass_context
def test(ctx, model_name, model_version, model_type, artifact_uri, test_query_uri, platform_type,
        timeout_in_ms, max_query_size_in_bytes, qps, waiting_model_ready_in_min, cpu_cores,
        memory_usage_in_mb, gpu_devices, fpga_devices, use_avx2, env_vars):
    """Run test in Polaris."""
    try:
        ctx.tracker.track_event('command', 'dlis_test')
        client = DlisApi()
        guid = client.test(
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            artifact_uri=artifact_uri,
            test_query_uri=test_query_uri,
            platform_type=platform_type,
            timeout_in_ms=timeout_in_ms,
            max_query_size_in_bytes=max_query_size_in_bytes,
            qps=qps,
            waiting_model_ready_in_min=waiting_model_ready_in_min,
            cpu_cores=cpu_cores,
            memory_usage_in_mb=memory_usage_in_mb,
            gpu_devices=gpu_devices,
            fpga_devices=fpga_devices,
            use_avx2=use_avx2,
            environment_vars=env_vars)
        if guid:
            ctx.log('Test submitted. TestID: {}.\nYou can see the task status by running:\n\t oml dlis show --id {}\n'
                'or go directly to http://lego.binginternal.com/polaris?any=DlisWebApi-{}'.format(guid, guid, guid))
    except Exception as e:
        ctx.tracker.track_event('exception', 'dlis_test')
        ctx.error_log(e)


@commands.command()
@click.option('-n', '--model-name', help='Model name.')
@click.option('-d', '--custom-model-name', help='Deploy using custom model name.')
@click.option('--model-version', help='Model version. Using latest version if not set.')
@click.option('-ns', '--namespace', help='Namespace. Can be set in oml.yml.')
@click.option('-e', '--environments', default='IndexServeDLModelServe2-Prod-CO4',
        help="""Environment names separated by semicolon. To see possible environments go to
        \b https://aka.ms/dlisendpoints (look for Environment Name) or
        https://aka.ms/dliscompliantendpoints (look for ObjectStore Environments column).""")
@click.option('-p', '--parallelism',
    help='Number of parallel threads per instance. Model must be threadsafe. Can be set in oml.yml. Default: 1')
@click.option('--instances', help='Number of instances. Either one value to use across environments, '
    'or one value per environment respectively, separated by semicolon. Can be set in oml.yml. Default: 1')
@click.option('-c', '--is-compliant', is_flag=True, default=None, hidden=True)
@click.option('-t', '--compliant-acl-allow',
    help='Certificate thumbprint(s) separated by semicolon. Required for compliant deployment.')
@click.option('--max-query-size-in-bytes', help='Maximum query size in bytes. Can be set in oml.yml.')
@click.option('--timeout-in-ms', help='Per-query timeout on the model. Can be set in oml.yml.')
@click.option('--waiting-model-ready-in-min', help='Model loading timeout. Can be set in oml.yml.')
@click.option('--cpu-cores', help='Number of CPU cores on each instance. Can be set in oml.yml. Default: 2')
@click.option('--memory-usage-in-mb', help='Reserved memory per instance in MB. Can be set in oml.yml. Default: 2048')
@click.option('--gpu-devices', help='Number of GPU devices on each instance. Can be set in oml.yml. Default: 0')
@click.option('--fpga-devices', help='Number of FGPA devices on each instance. Can be set in oml.yml. Default: 0')
@click.option('--use-avx2/--no-use-avx2', is_flag=True, default=None,
    help='Whether to use AVX2. Compliant only. Can be set in oml.yml. Default: False')
@click.option('--env-vars',
    help='Environment variables to use, separated with semicolon in NAME=value format. Can be set in oml.yml')
@click.option('--force-replace/--force-create', is_flag=True, default=None, hidden=True)
@click.option('--replace-version', default=None, type=int, hidden=True)
@pass_context
def deploy(ctx, model_name, custom_model_name, model_version, namespace,
        environments, parallelism, instances, is_compliant, compliant_acl_allow,
        max_query_size_in_bytes, timeout_in_ms, waiting_model_ready_in_min, cpu_cores, memory_usage_in_mb,
        gpu_devices, fpga_devices, use_avx2, env_vars, force_replace, replace_version):
    """Deploy model to inferencing."""
    try:
        ctx.tracker.track_event('command', 'dlis_deploy')
        client = DlisApi()
        guid = client.deploy(
            model_name=model_name,
            custom_model_name=custom_model_name,
            model_version=model_version,
            namespace=namespace,
            environments=environments,
            parallelism=parallelism,
            instances=instances,
            is_compliant=is_compliant,
            compliant_acl_allow=compliant_acl_allow,
            max_query_size_in_bytes=max_query_size_in_bytes,
            timeout_in_ms=timeout_in_ms,
            waiting_model_ready_in_min=waiting_model_ready_in_min,
            cpu_cores=cpu_cores,
            memory_usage_in_mb=memory_usage_in_mb,
            gpu_devices=gpu_devices,
            fpga_devices=fpga_devices,
            use_avx2=use_avx2,
            environment_vars=env_vars,
            force_replace=force_replace,
            replace_version=replace_version)
        if guid:
            comp_desc = '\nAfter the task shows "Status: Succeeded", expect an Azure Task email within the next hour.' \
                '\nSomeone from your team that is a part of the security group listed for the DLIS namespace must ' \
                'approve by writing "Approved" in the Discussion section of the task.'
            ctx.log('Task submitted. DeploymentID: {}.\nYou can see the task status by running:'
                    '\n\toml dlis show -r deployment --id {} {}'
                    .format(guid, guid, comp_desc if is_compliant else ''))
    except Exception as e:
        ctx.tracker.track_event('exception', 'dlis_deploy')
        ctx.error_log(e)


@commands.command()
@pass_context
def manifest(ctx):
    """Generate the manifests."""
    try:
        ctx.tracker.track_event('command', 'dlis_manifest')
        model = Model(os.getcwd(), ctx.verbose)
        model.create_manifests()
    except Exception as e:
        ctx.tracker.track_event('exception', 'dlis_manifest')
        ctx.error_log(e)
