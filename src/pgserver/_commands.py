from pathlib import Path
import sys
import subprocess
from typing import Optional, List, Callable
import logging
import tempfile

# Base path for PostgreSQL installation
POSTGRES_INSTALL_BASE = Path(__file__).parent / "pginstall"
POSTGRES_BIN_PATH = POSTGRES_INSTALL_BASE / "bin"

def _detect_installed_version() -> Optional[int]:
    """Detect which PostgreSQL version is installed by reading PG_VERSION file.

    Returns:
        The major version number, or None if not found
    """
    version_file = POSTGRES_INSTALL_BASE / "share" / "postgresql" / "PG_VERSION"
    if not version_file.exists():
        return None

    try:
        version_str = version_file.read_text().strip()
        # PG_VERSION contains just the major version number (e.g., "16", "17", "18")
        return int(version_str)
    except (ValueError, OSError):
        return None

# Detect installed version
INSTALLED_POSTGRES_VERSION = _detect_installed_version()

# For backward compatibility, expose these constants
# They will be None if no PostgreSQL is installed (which shouldn't happen in a valid package)
DEFAULT_POSTGRES_VERSION = INSTALLED_POSTGRES_VERSION
AVAILABLE_POSTGRES_VERSIONS = [INSTALLED_POSTGRES_VERSION] if INSTALLED_POSTGRES_VERSION else []

def get_postgres_bin_path() -> Path:
    """Get the binary path for the installed PostgreSQL version.

    Returns:
        Path to the bin directory

    Raises:
        FileNotFoundError: If PostgreSQL binaries are not found
    """
    if not POSTGRES_BIN_PATH.exists():
        raise FileNotFoundError(
            f"PostgreSQL binaries not found at {POSTGRES_BIN_PATH}. "
            "The package may not have been installed correctly."
        )

    return POSTGRES_BIN_PATH

_logger = logging.getLogger('pgserver')

def create_command_function(pg_exe_name : str) -> Callable:
    def command(args : List[str], pgdata : Optional[Path] = None, **kwargs) -> str:
        """
            Run a command with the given command line arguments.
            Args:
                args: The command line arguments to pass to the command as a string,
                a list of options as would be passed to `subprocess.run`
                pgdata: The path to the data directory to use for the command.
                    If the command does not need a data directory, this should be None.
                kwargs: Additional keyword arguments to pass to `subprocess.run`, eg user, timeout.

            Returns:
                The stdout of the command as a string.
        """
        if pg_exe_name.strip('.exe') in ['initdb', 'pg_ctl', 'pg_dump']:
           assert pgdata is not None, "pgdata must be provided for initdb, pg_ctl, and pg_dump"

        if pgdata is not None:
            args = ["-D", str(pgdata)] + args

        full_command_line = [str(POSTGRES_BIN_PATH / pg_exe_name)] + args

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