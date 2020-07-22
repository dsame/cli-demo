import click
import traceback

from oml.context import pass_context
from oml.platforms.azureml import AzureMlApi


@click.group('azureml')
def commands():
    """AzureML operation commands."""
    pass


@commands.command()
@click.option('-w', '--workspace', help='Workspace name prefix ("-{region}" will be appended to the workspace name).')
@click.option('-r', '--regions', help='Comma separated list of Azure regions, e.g. WestUS,EastUS,NorthEurope. '
              'First region in the list is where other resources will be created.')
@click.option('-rg', '--resource-group', help='Resource group name. Will be created if it doesn\'t exist. '
              'Defaults to \'aml-rg-<workspace name>\'.')
@click.option('-s', '--subscription-id', help='Azure subscription id or name.')
@click.option('--primary-workspace-name',
              help='Created workspaces should use the attached resources from this primary workspace.')
@pass_context
def provision(ctx, workspace, regions, resource_group, subscription_id, primary_workspace_name):
    """Provision AzureML Workspace and required resources."""
    try:
        ctx.tracker.track_event('command', 'azureml_provision')
        client = AzureMlApi()
        client.create_workspace(
            workspace,
            regions,
            resource_group,
            subscription_id,
            primary_workspace_name)
        ctx.log('Workspaces provisioned')
    except Exception as e:
        ctx.tracker.track_event('exception', 'azureml_provision')
        ctx.error_log(e)


@commands.command()
@click.option('--certificate-file',
              help='Local path to the certificate file to be used for mTLS. '
              'Must provide this or certificate-url.')
@click.option('--certificate-url',
              help='KeyVault url to the certificate to be used for mTLS. '
              'Must provide this or certificate-file.')
@pass_context
def fingerprint(ctx, certificate_file, certificate_url):
    """Generate the SHA-256 fingerprint to be used for mTLS deployment configuration."""
    try:
        ctx.tracker.track_event('command', 'azureml_fingerprint')
        client = AzureMlApi()
        print(client.generate_fingerprint(certificate_file, certificate_url))
    except Exception as e:
        traceback.print_stack()
        ctx.tracker.track_event('exception', 'azureml_fingerprint')
        ctx.error_log(e)


@commands.command()
@click.option('-w', '--workspace', required=True, help='Workspace name.')
@click.option('-rg', '--resource-group', required=True, help='Resource group name.')
@click.option('-s', '--subscription-id', required=True, help='Azure subscription id or name.')
@click.option('--model-name', required=True, help='Name of the model to deploy.')
@click.option('--service-name', required=True, help='Name of the service to create.')
@click.option('--inference-config-file', required=True, type=click.Path(exists=True),
              help='Local path to the inference config file.')
@click.option('--deployment-config-file', required=True, type=click.Path(exists=True),
              help='Local path to the deployment config file.')
@click.option('--signing-certificate-file',
              help='Local path to the certificate file to be used for deployment request signing. '
              'Must provide this or signing-certificate-url.')
@click.option('--signing-certificate-url',
              help='KeyVault url to the certificate to be used for deployment request signing. '
              'Must provide this or signing-certificate-file.')
@click.option('--overwrite', is_flag=True, help='Delete the existing deployed service if it already exists. '
              'Use of this flag may be destructive.')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
@pass_context
def deploy(ctx,
           workspace,
           resource_group,
           subscription_id,
           model_name,
           service_name,
           inference_config_file,
           deployment_config_file,
           signing_certificate_file,
           signing_certificate_url,
           overwrite,
           verbose):
    """Deploy model to inferencing."""
    try:
        ctx.tracker.track_event('command', 'azureml_deploy')
        client = AzureMlApi()
        client.deploy(workspace,
                      resource_group,
                      subscription_id,
                      model_name,
                      service_name,
                      inference_config_file,
                      deployment_config_file,
                      signing_certificate_file,
                      signing_certificate_url,
                      overwrite,
                      verbose)
    except Exception as e:
        if verbose:
            traceback.print_stack()
        ctx.tracker.track_event('exception', 'azureml_deploy')
        ctx.error_log(e)
