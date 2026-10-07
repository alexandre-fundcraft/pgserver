![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
![Postgres Version](https://img.shields.io/badge/PostgreSQL-17%20%7C%2018-blue)

![Linux ARM64 Support](https://img.shields.io/badge/Linux%20ARM64%20Support-manylinux-green)
![macOS Apple Silicon Support >=11](https://img.shields.io/badge/macOS%20Apple%20Silicon%20Support-%E2%89%A511(BigSur)-green)

[![License](https://img.shields.io/badge/License-Apache%202.0-darkblue.svg)](https://opensource.org/licenses/Apache-2.0)


<p align="center">
  <img src="https://raw.githubusercontent.com/orm011/pgserver/main/pgserver_square_small.png"/>
</p>

# pgserver: pip-installable, embedded postgres server + pgvector extension for your python app

`pgserver` lets you build Postgres-backed python apps with the same convenience afforded by an embedded database (ie, alternatives such as sqlite). 
If you build your app with pgserver, your app remains wholly pip-installable, saving your users from needing to understand how to setup a postgres server (they simply pip install your app, and postgres is brought in through dependencies), and letting you get started developing quickly: just install the wheels (see [Installation](#installation-and-postgresql-version)) and call `pgserver.get_server(...)`, as shown in this notebook: <a target="_blank" href="https://colab.research.google.com/github/orm011/pgserver/blob/master/pgserver-example.ipynb"> <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/> </a> 

To achieve this, you need two things which `pgserver` provides
  * python binary wheels for multiple-plaforms with postgres binaries
  * convenience python methods that handle db initialization and server process management, that deals with things that would normally prevent you from running your python app seamlessly on environments like docker containers, a machine you have no root access in, machines with other running postgres servers, google colab, etc.  One main goal of the project is robustness around this.

Additionally, this package includes the [pgvector](https://github.com/pgvector/pgvector) postgres extension, useful for storing associated vector data and for vector similarity queries.

## Basic summary:
* _Pip installable binaries_: built and tested on Linux ARM64 (manylinux) and macOS Apple Silicon, with Python 3.11 to 3.14.
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

Wheels are published on [GitHub releases](https://github.com/alexandre-fundcraft/pgserver/releases), not on PyPI. Each version has its own release (`v0.3.0` below); `latest` is rebuilt on every push to `develop`.
Install the main package (pure Python) together with one binary package for your PostgreSQL version and platform.
PostgreSQL 17 and 18 are available, each with pgvector, for Linux ARM64 and macOS Apple Silicon:

```bash
# Linux ARM64 (e.g. Docker on Apple Silicon), PostgreSQL 18
pip install \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.3.0/pgserver-0.3.0-py3-none-any.whl \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.3.0/pgserver_postgres_18-0.3.0-py3-none-manylinux_2_17_aarch64.whl

# macOS Apple Silicon, PostgreSQL 18
pip install \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.3.0/pgserver-0.3.0-py3-none-any.whl \
  https://github.com/alexandre-fundcraft/pgserver/releases/download/v0.3.0/pgserver_postgres_18-0.3.0-py3-none-macosx_11_0_arm64.whl
```

For PostgreSQL 17, replace `pgserver_postgres_18` with `pgserver_postgres_17`.

Check which version is installed:
```py
import pgserver
print(f"PostgreSQL version: {pgserver.INSTALLED_POSTGRES_VERSION}")
```

**How it works:** The main `pgserver` package contains only Python code. PostgreSQL binaries are provided by separate packages (`pgserver-postgres-17`, `pgserver-postgres-18`). Install exactly one of them next to `pgserver`.

Postgres binaries in the package can be found in the directory pointed
to by the `pgserver.POSTGRES_BIN_PATH` to be used directly.

This project was originally based on [](https://github.com/michelp/postgresql-wheel), which provides a linux wheel.
But adds the following differences:
1. binary wheels for Linux ARM64 and macOS Apple Silicon
2. postgres python management: cross-platfurm startup and cleanup including many edge cases, runs on colab etc.
3. includes `pgvector` extension but currently excludes `postGIS`
