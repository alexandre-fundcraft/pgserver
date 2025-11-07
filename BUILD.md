# Building pgserver Packages

This document explains how to build the pgserver packages locally and via CI/CD.

## Package Structure

The project consists of 4 packages:

1. **pgserver** - Main package (Python code only)
2. **pgserver-postgres-16** - PostgreSQL 16.10 + pgvector 0.8.0 binaries
3. **pgserver-postgres-17** - PostgreSQL 17.6 + pgvector 0.8.0 binaries
4. **pgserver-postgres-18** - PostgreSQL 18.0 + pgvector 0.8.0 binaries

## Quick Start - Local Build & Test

```bash
# Build all packages
./build-local.sh

# Test all packages
./test-local.sh
```

## Manual Local Build

### Prerequisites

- Python 3.9+
- C compiler (gcc, clang, or MSVC)
- Make
- curl
- Standard build tools for your platform

### Build Steps

#### 1. Build Binary Packages

Each binary package must be built separately:

```bash
# PostgreSQL 18
cd packages/pgserver-postgres-18
make build
python -m build --wheel
cd ../..

# PostgreSQL 17
cd packages/pgserver-postgres-17
make build
python -m build --wheel
cd ../..

# PostgreSQL 16
cd packages/pgserver-postgres-16
make build
python -m build --wheel
cd ../..
```

This creates wheels in `packages/*/dist/`.

#### 2. Build Main Package

```bash
# Remove any binaries from main package
rm -rf src/pgserver/pginstall

# Build wheel
python -m build --wheel
```

This creates the main package wheel in `dist/`.

### Testing Locally

```bash
# Create virtual environment
python -m venv test-env
source test-env/bin/activate  # or test-env\Scripts\activate on Windows

# Install desired version
pip install packages/pgserver-postgres-18/dist/*.whl  # Choose 16, 17, or 18
pip install dist/*.whl

# Test
python -c "import pgserver; print(f'PostgreSQL {pgserver.INSTALLED_POSTGRES_VERSION}')"
```

## CI/CD Build

The GitHub Actions workflow (`.github/workflows/build-and-test.yml`) automatically:

1. Builds all 3 binary packages (PG 16, 17, 18) on multiple platforms:
   - macOS x86_64 (Intel)
   - macOS arm64 (Apple Silicon)
   - Ubuntu x86_64 (manylinux)
   - Windows AMD64

2. Builds the main package (platform-independent)

3. On tagged releases, publishes all 4 packages to PyPI

### Trigger CI Build

```bash
# Push to testing or main branch
git push origin main

# Or manually trigger
# Go to Actions tab on GitHub → Build and Test → Run workflow
```

## Build Configuration

### Environment Variables

- `PGSERVER_VERSION`: PostgreSQL major version to build (16, 17, or 18)
  ```bash
  PGSERVER_VERSION=17 make -C pgbuild
  ```

- `MACOSX_DEPLOYMENT_TARGET`: Minimum macOS version (set automatically by CI)

### Build Outputs

Binary packages install PostgreSQL to:
```
packages/pgserver-postgres-*/src/pgserver_binaries/pg*/
  ├── bin/          # PostgreSQL executables
  ├── lib/          # Libraries including pgvector
  ├── share/        # Documentation and PG_VERSION file
  └── include/      # Header files
```

At runtime, pgserver searches site-packages for `pgserver_binaries/pg*/`.

## Troubleshooting

### Build fails with "PostgreSQL binaries not found"

Make sure you run `make build` in the binary package directory before `python -m build`.

### Import error: "No module named 'pgserver_binaries'"

Install one of the binary packages first:
```bash
pip install packages/pgserver-postgres-18/dist/*.whl
```

### Version mismatch

Uninstall all packages and reinstall:
```bash
pip uninstall -y pgserver pgserver-postgres-16 pgserver-postgres-17 pgserver-postgres-18
pip install <desired-package>.whl
```

## Publishing to PyPI

**Note:** Publishing requires maintainer access.

1. Binary packages must be published **before** the main package
2. All packages should have the same version number
3. Use GitHub releases with tags to trigger automatic publishing

```bash
# Create release
git tag v0.1.5
git push origin v0.1.5
# GitHub Actions will build and publish all packages
```

Packages will be available as:
- `pip install pgserver` → PostgreSQL 18 (default)
- `pip install "pgserver[pg16]"` → PostgreSQL 16
- `pip install "pgserver[pg17]"` → PostgreSQL 17
