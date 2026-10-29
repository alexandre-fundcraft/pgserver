![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
![Postgres Version](https://img.shields.io/badge/PostgreSQL-17%20%7C%2018-blue)

![Linux ARM64 Support](https://img.shields.io/badge/Linux%20ARM64%20Support-manylinux-green)
![Linux x86_64 Support](https://img.shields.io/badge/Linux%20x86__64%20Support-manylinux-green)
![macOS Apple Silicon Support >=11](https://img.shields.io/badge/macOS%20Apple%20Silicon%20Support-%E2%89%A511(BigSur)-green)

[![License](https://img.shields.io/badge/License-Apache%202.0-darkblue.svg)](https://opensource.org/licenses/Apache-2.0)


<p align="center">
  <img src="https://raw.githubusercontent.com/orm011/pgserver/main/pgserver_square_small.png"/>
</p>

# pgserver: pip-installable, embedded postgres server + contrib & pgvector extensions

> **Maintained Fork**: This repository is an independent, modernized fork of [orm011/pgserver](https://github.com/orm011/pgserver) maintained in a personal capacity by **Alexandre Busquets Triola**.  
> It adds support for **PostgreSQL 17 and 18**, **Python 3.11 to 3.14**, multi-architecture wheels (**macOS Apple Silicon, Linux ARM64, and Linux x86_64**), bundled standard PostgreSQL **`contrib/` extensions** (`btree_gist`, `unaccent`, `pg_trgm`, `pgcrypto`, etc.) alongside `pgvector`, and macOS `@rpath` binary relocation.  
> **⚠️ Disclaimer & No Liability**: This software and its pre-built binaries are provided strictly **"AS IS"**, without warranty or support of any kind, and for local development/testing purposes only. Neither the maintainer nor any affiliated organization assumes any responsibility or liability for any damages, data loss, security incidents, or issues arising from its use. See [Disclaimer, No Warranty & Limitation of Liability](#disclaimer-no-warranty--limitation-of-liability) below.

`pgserver` lets you build Postgres-backed python apps with the same convenience afforded by an embedded database (ie, alternatives such as sqlite). 
If you build your app with pgserver, your app remains wholly pip-installable, saving your users from needing to understand how to setup a postgres server (they simply pip install your app, and postgres is brought in through dependencies), and letting you get started developing quickly: just install the wheels (see [Installation](#installation-and-postgresql-version)) and call `pgserver.get_server(...)`, as shown in this notebook: <a target="_blank" href="https://colab.research.google.com/github/orm011/pgserver/blob/master/pgserver-example.ipynb"> <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/> </a> 

To achieve this, you need two things which `pgserver` provides
  * python binary wheels for multiple-plaforms with postgres binaries
  * convenience python methods that handle db initialization and server process management, that deals with things that would normally prevent you from running your python app seamlessly on environments like docker containers, a machine you have no root access in, machines with other running postgres servers, google colab, etc.  One main goal of the project is robustness around this.

Additionally, this package includes the [pgvector](https://github.com/pgvector/pgvector) postgres extension, useful for storing associated vector data and for vector similarity queries.

## Basic summary:
* _Pip installable binaries_: built and tested on Linux ARM64 (manylinux), Linux x86_64 (manylinux) and macOS Apple Silicon, with Python 3.11 to 3.14.
* _No sudo or admin rights needed_: Does not require `root` privileges or `sudo`.
* but... _can handle root_: in some environments your python app runs as root, eg docker, google colab, `pgserver` handles this case.
* _Simpler initialization_: `pgserver.get_server(MY_DATA_DIR)` method to initialize data and server if needed, so you don't need to understand `initdb`, `pg_ctl`, port conflicts.
* _Convenient cleanup_: server process cleanup is done for you: when the process using pgserver ends, the server is shutdown, including when multiple independent processes call
`pgserver.get_server(MY_DATA_DIR)` on the same dir (wait for last one). You can blow away your PGDATA dir and start again.
* For lower-level control, wrappers to all binaries, such as `initdb`, `pg_ctl`, `psql`, `pg_config`. Includes header files in case you wish to build some other extension and use it against these binaries.

```py
# Example 1: postgres backed application
import pgserver

db = pgserver.get_server(MYPGDATA)
# server ready for connection.

print(db.psql('create extension vector'))
db_uri = db.get_uri()
# use uri with sqlalchemy / psycopg, etc, see colab.

# if no other process is using this server, it will be shutdown at exit,
# if other process use same pgadata, server process will be shutdown when all stop.
```

```py
# Example 2: Testing
import tempfile
import pytest
@pytest.fixture
def tmp_postgres():
    tmp_pg_data = tempfile.mkdtemp()
    pg = pgserver.get_server(tmp_pg_data, cleanup_mode='stop')
    yield pg
    pg.cleanup()
```

## Installation and PostgreSQL version

Wheels are published on [GitHub releases](https://github.com/alexandre-fundcraft/pgserver/releases), not on PyPI. Each version has its own release (`v0.4.0` below); `latest` is rebuilt on every push to `develop`.
Install the main package (pure Python) together with one binary package for your PostgreSQL version and platform.
PostgreSQL 17 and 18 are available, bundled with standard PostgreSQL `contrib` extensions (`btree_gist`, `unaccent`, `pg_trgm`, `pgcrypto`, etc.) alongside `pgvector`, for Linux ARM64, Linux x86_64 and macOS Apple Silicon.

### Using `pip`

```bash
# Linux ARM64 (e.g. Docker on Apple Silicon), PostgreSQL 18
pip install \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver-0.4.0-py3-none-any.whl \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_18-0.4.0-py3-none-manylinux_2_17_aarch64.whl

# Linux x86_64, PostgreSQL 18
pip install \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver-0.4.0-py3-none-any.whl \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_18-0.4.0-py3-none-manylinux_2_17_x86_64.whl

# macOS Apple Silicon, PostgreSQL 18
pip install \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver-0.4.0-py3-none-any.whl \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_18-0.4.0-py3-none-macosx_11_0_arm64.whl
```

For PostgreSQL 17, replace `pgserver_postgres_18` with `pgserver_postgres_17`.

### Using `uv` (`pyproject.toml`)

```toml
[dependency-groups]
local = [
    "pgserver==0.4.0; (sys_platform == 'darwin' and platform_machine == 'arm64') or (sys_platform == 'linux' and platform_machine in ('aarch64', 'x86_64'))",
    "pgserver-postgres-17==0.4.0; (sys_platform == 'darwin' and platform_machine == 'arm64') or (sys_platform == 'linux' and platform_machine in ('aarch64', 'x86_64'))",
]

[tool.uv.sources]
pgserver = { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver-0.4.0-py3-none-any.whl", marker = "(sys_platform == 'darwin' and platform_machine == 'arm64') or (sys_platform == 'linux' and platform_machine in ('aarch64', 'x86_64'))" }
pgserver-postgres-17 = [
    { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_17-0.4.0-py3-none-macosx_11_0_arm64.whl", marker = "sys_platform == 'darwin' and platform_machine == 'arm64'" },
    { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_17-0.4.0-py3-none-manylinux_2_17_aarch64.whl", marker = "sys_platform == 'linux' and platform_machine == 'aarch64'" },
    { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_17-0.4.0-py3-none-manylinux_2_17_x86_64.whl", marker = "sys_platform == 'linux' and platform_machine == 'x86_64'" },
]
```

Then install with:
```bash
uv sync --group local
```

### Using `Poetry` (`pyproject.toml`)

```toml
[tool.poetry.group.local.dependencies]
pgserver = { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver-0.4.0-py3-none-any.whl" }
pgserver-postgres-17 = [
    { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_17-0.4.0-py3-none-macosx_11_0_arm64.whl", markers = "sys_platform == 'darwin' and platform_machine == 'arm64'" },
    { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_17-0.4.0-py3-none-manylinux_2_17_aarch64.whl", markers = "sys_platform == 'linux' and platform_machine == 'aarch64'" },
    { url = "https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.4.0/pgserver_postgres_17-0.4.0-py3-none-manylinux_2_17_x86_64.whl", markers = "sys_platform == 'linux' and platform_machine == 'x86_64'" },
]
```

Then install with:
```bash
poetry install --with local
```

Check which version is installed:
```py
import pgserver
print(f"PostgreSQL version: {pgserver.INSTALLED_POSTGRES_VERSION}")
```

**How it works:** The main `pgserver` package contains only Python code. PostgreSQL binaries are provided by separate packages (`pgserver-postgres-17`, `pgserver-postgres-18`). Install exactly one of them next to `pgserver`.

Postgres binaries in the package can be found in the directory pointed
to by the `pgserver.POSTGRES_BIN_PATH` to be used directly.

This repository is maintained by **Alexandre Busquets Triola** as a fork of [orm011/pgserver](https://github.com/orm011/pgserver) (originally based on [postgresql-wheel](https://github.com/michelp/postgresql-wheel)), adding:
1. Up-to-date PostgreSQL versions: **PostgreSQL 17 and 18** (upstream stopped at PG 16)
2. Tested across **Python 3.11, 3.12, 3.13, and 3.14**
3. Multi-platform binary wheels for **macOS Apple Silicon (arm64)**, **Linux ARM64 (aarch64)**, and **Linux x86_64**
4. Bundled standard PostgreSQL **`contrib` extensions** (`btree_gist`, `unaccent`, `pg_trgm`, `pgcrypto`, `citext`, etc.) alongside `pgvector`
5. macOS `@rpath` binary relocation so embedded clusters run without build-machine absolute path dependencies

## Disclaimer, No Warranty & Limitation of Liability

- **Provided "AS IS" without warranty**: In accordance with Sections 7 and 8 of the [Apache License 2.0](LICENSE), all source code, build scripts, and pre-compiled binary wheels in this repository and its releases are provided on an **"AS IS"** and **"AS AVAILABLE"** basis, without warranties or conditions of any kind, either express or implied, including, without limitation, any warranties or conditions of title, non-infringement, merchantability, fitness for a particular purpose, security, or accuracy.
- **Complete limitation of liability**: In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, shall **Alexandre Busquets Triola**, any contributor, or any current or former employer or affiliated organization be liable to you or any third party for any direct, indirect, special, incidental, consequential, exemplary, or punitive damages of any character (including, without limitation, damages for loss of data, database corruption, security breaches, loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses) arising out of or relating to the use of, or inability to use, this software or its binary distributions, even if advised of the possibility of such damages.
- **Personal capacity & non-affiliation**: This fork is maintained independently in a personal capacity. It is not an official product, service, or supported offering of any employer, company, or organization.
- **Development & testing use only**: This package runs an embedded local PostgreSQL instance intended for local development, prototyping, and automated test suites. It is **not** designed, audited, or hardened for production database workloads. You assume full and sole responsibility for evaluating, auditing, and verifying the suitability and security of any code or binaries you download and execute.
- **No support or maintenance obligation**: There is no commitment, SLA, or obligation to provide technical support, bug fixes, security updates, or future releases.
- **Third-party components**: Pre-built binary wheels bundle upstream [PostgreSQL](https://www.postgresql.org/about/licence/) and [pgvector](https://github.com/pgvector/pgvector/blob/master/LICENSE), which are governed by the PostgreSQL License and carry their own respective disclaimers of warranty and liability.
