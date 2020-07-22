import click
import sys
import traceback

from oml.hooks.appinsights import AppInsightsHook
from oml.util.shell import run_shell


class Context:

    def __init__(self):
        self.verbose = False
        self.tracker = AppInsightsHook()

    def log(self, msg, verbose=False):
        """Logs a message to stdout."""
        click.echo(msg, err=verbose)

    def vlog(self, msg):
        """Logs a verbose message to stderr"""
        if self.verbose:
            self.log(msg, True)

    def error_log(self, msg):
        if self.verbose:
            traceback.print_exc()
        else:
            click.secho('::[Error]:: {}'.format(msg), fg='red')
        sys.exit(1)

    def is_outdated(self):
        out = run_shell(['pip', 'list', '-o'], capture_output=True)
        out_list = out.split()
        if 'oml' in out_list:
            idx = out_list.index('oml')
            old_version = out_list[idx + 1]
            new_version = out_list[idx + 2]
            click.secho('You are using oml version {}, however version {} is available.'
                .format(old_version, new_version), fg='yellow')
            click.secho('You should consider upgrading via the `pip install -U oml` command.', fg='yellow')


pass_context = click.make_pass_decorator(Context, ensure=True)
