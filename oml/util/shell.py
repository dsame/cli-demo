import os
import subprocess  # nosec

from oml.exceptions import OMLException
from oml.settings import EXEC_BASE_PATH


def exec_dotnet(cmd):
    try:
        run_shell(['dotnet'] + cmd)
    except Exception:
        raise OMLException('Failed to run dotnet.')


def exec_nuget(cmd):
    nuget_exe = [os.path.join(EXEC_BASE_PATH, 'NuGet.exe')]
    try:
        run_shell(nuget_exe + cmd)
    except Exception:
        raise OMLException('Failed to run NuGet.exe.')


def exec_scope(cmd):
    scope_exe = [os.path.join(EXEC_BASE_PATH, 'scope', 'Scope.exe')]
    try:
        run_shell(scope_exe + cmd)
    except Exception:
        raise OMLException('Failed to run Scope.exe.')


def exec_aether(cmd):
    aether_exe = [os.path.join(EXEC_BASE_PATH, 'aether', 'AetherDeploy.exe')]
    try:
        run_shell(aether_exe + cmd)
    except Exception as e:
        raise OMLException(e)


def exec_powershell(cmd):
    try:
        run_shell(['powershell.exe'] + ['-ExecutionPolicy', 'Bypass', '-File'] + cmd)
    except Exception as e:
        raise OMLException(e)


def run_shell(cmd, capture_output=False):
    if capture_output:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)  # nosec
        return res.stdout.decode('utf-8')
    else:
        return subprocess.run(cmd, check=True)  # nosec
