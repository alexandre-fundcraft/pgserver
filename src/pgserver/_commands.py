from pathlib import Path
import sys
import subprocess
from typing import Optional, List, Callable, Dict
import logging
import tempfile

# Base path for PostgreSQL installations
POSTGRES_INSTALL_BASE = Path(__file__).parent / "pginstall"

# Default PostgreSQL version
DEFAULT_POSTGRES_VERSION = 18

# Available PostgreSQL versions
AVAILABLE_POSTGRES_VERSIONS = [16, 17, 18]

def get_postgres_bin_path(version: int = DEFAULT_POSTGRES_VERSION) -> Path:
    """Get the binary path for a specific PostgreSQL version.

    Args:
        version: PostgreSQL major version (16, 17, or 18)

    Returns:
        Path to the bin directory for the specified version

    Raises:
        ValueError: If the version is not supported
    """
    if version not in AVAILABLE_POSTGRES_VERSIONS:
        raise ValueError(
            f"PostgreSQL version {version} is not supported. "
            f"Available versions: {AVAILABLE_POSTGRES_VERSIONS}"
        )

    bin_path = POSTGRES_INSTALL_BASE / f"pg{version}" / "bin"

    if not bin_path.exists():
        raise FileNotFoundError(
            f"PostgreSQL {version} binaries not found at {bin_path}. "
            "The package may not have been built correctly."
        )

    return bin_path

# Keep backward compatibility - default to version 18
POSTGRES_BIN_PATH = get_postgres_bin_path(DEFAULT_POSTGRES_VERSION)

_logger = logging.getLogger('pgserver')

def create_command_function(pg_exe_name : str) -> Callable:
    def command(args : List[str], pgdata : Optional[Path] = None, postgres_version: int = DEFAULT_POSTGRES_VERSION, **kwargs) -> str:
        """
            Run a command with the given command line arguments.
            Args:
                args: The command line arguments to pass to the command as a string,
                a list of options as would be passed to `subprocess.run`
                pgdata: The path to the data directory to use for the command.
                    If the command does not need a data directory, this should be None.
                postgres_version: PostgreSQL major version to use (16, 17, or 18). Defaults to 18.
                kwargs: Additional keyword arguments to pass to `subprocess.run`, eg user, timeout.

            Returns:
                The stdout of the command as a string.
        """
        if pg_exe_name.strip('.exe') in ['initdb', 'pg_ctl', 'pg_dump']:
           assert pgdata is not None, "pgdata must be provided for initdb, pg_ctl, and pg_dump"

        if pgdata is not None:
            args = ["-D", str(pgdata)] + args

        # Get the version-specific bin path
        bin_path = get_postgres_bin_path(postgres_version)
        full_command_line = [str(bin_path / pg_exe_name)] + args

        with tempfile.TemporaryFile('w+') as stdout, tempfile.TemporaryFile('w+') as stderr:
            try:
                _logger.info("Running commandline:\n%s\nwith kwargs: `%s`", full_command_line, kwargs)
                # NB: capture_output=True, as well as using stdout=subprocess.PIPE and stderr=subprocess.PIPE
                # can cause this call to hang, even with a time-out depending on the command, (pg_ctl)
                # so we use two temporary files instead
                result = subprocess.run(full_command_line, check=True, stdout=stdout, stderr=stderr, text=True,
                                        **kwargs)
                stdout.seek(0)
                stderr.seek(0)
                output = stdout.read()
                error = stderr.read()
                _logger.info("Successful postgres command %s with kwargs: `%s`\nstdout:\n%s\n---\nstderr:\n%s\n---\n",
                            result.args, kwargs, output, error)
            except subprocess.CalledProcessError as err:
                stdout.seek(0)
                stderr.seek(0)
                output = stdout.read()
                error = stderr.read()
                _logger.error("Failed postgres command %s with kwargs: `%s`:\nerror:\n%s\nstdout:\n%s\n---\nstderr:\n%s\n---\n",
                            err.args, kwargs, str(err), output,  error)
                raise err

        return output

    return command

__all__ = []
def _init():
    for path in POSTGRES_BIN_PATH.iterdir():
        exe_name = path.name
        prog = create_command_function(exe_name)
        # Strip .exe suffix for Windows compatibility
        function_name = exe_name.strip('.exe')
        setattr(sys.modules[__name__], function_name, prog)
        __all__.append(function_name)

_init()