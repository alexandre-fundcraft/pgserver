# Changelog

## [0.3.0] - 2026-10-07

### Changed
- Binary wheels are built for PostgreSQL 17 and 18 only, on Linux ARM64 and macOS Apple Silicon; PostgreSQL 16 is dropped (`pg16` extra and `pgserver-postgres-16` package removed)
- Wheels are published on GitHub releases instead of PyPI
- Every build is tested on Python 3.11, 3.12, 3.13 and 3.14 before it is published

### Fixed
- macOS binaries no longer reference the build machine's paths, so `initdb` runs on any Mac

## [0.2.0] - 2025-11-07

### Added
- Support for PostgreSQL 17 and 18 (in addition to existing PostgreSQL 16)
- Multi-version architecture with separate binary packages:
  - `pgserver-postgres-16` - PostgreSQL 16.10 binaries
  - `pgserver-postgres-17` - PostgreSQL 17.6 binaries
  - `pgserver-postgres-18` - PostgreSQL 18.0 binaries
- Version selection via pip extras:
  - `pip install pgserver` - installs PostgreSQL 18 (default)
  - `pip install "pgserver[pg16]"` - installs PostgreSQL 16
  - `pip install "pgserver[pg17]"` - installs PostgreSQL 17
- `INSTALLED_POSTGRES_VERSION` constant to check which version is installed

### Changed
- Main `pgserver` package is now a universal wheel (py3-none-any) compatible with all Python 3.9+ versions
- Binary packages are distributed separately from Python code, reducing download size
- Upgraded pgvector extension to v0.8.1 for PostgreSQL 18 compatibility
- PostgreSQL binaries now use RPATH to find bundled libraries, preventing conflicts with system PostgreSQL installations
