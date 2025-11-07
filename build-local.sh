#!/bin/bash
# Local build script for testing pgserver packages

set -e  # Exit on error

echo "=== Building pgserver packages locally ==="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ wheelhouse/ *.egg-info
rm -rf packages/*/dist packages/*/build packages/*/*.egg-info
make -C pgbuild clean

# Build binary package for PostgreSQL 18 (default)
echo ""
echo "=== Building pgserver-postgres-18 ==="
cd packages/pgserver-postgres-18
make clean
make build
python -m pip install build
python -m build --wheel
cd ../..

# Build binary package for PostgreSQL 16
echo ""
echo "=== Building pgserver-postgres-16 ==="
cd packages/pgserver-postgres-16
make clean
make build
python -m build --wheel
cd ../..

# Build binary package for PostgreSQL 17
echo ""
echo "=== Building pgserver-postgres-17 ==="
cd packages/pgserver-postgres-17
make clean
make build
python -m build --wheel
cd ../..

# Build main package (no binaries, just Python code)
echo ""
echo "=== Building main pgserver package ==="
# Remove pginstall directory since main package shouldn't include binaries
rm -rf src/pgserver/pginstall
python -m build --wheel

echo ""
echo "=== Build complete! ==="
echo ""
echo "Wheels created:"
ls -lh packages/*/dist/*.whl dist/*.whl 2>/dev/null || true

echo ""
echo "To test locally:"
echo "  # Create a virtual environment"
echo "  python -m venv test-env"
echo "  source test-env/bin/activate  # or test-env\\Scripts\\activate on Windows"
echo ""
echo "  # Install pgserver with PostgreSQL 18 (default)"
echo "  pip install packages/pgserver-postgres-18/dist/*.whl"
echo "  pip install dist/*.whl"
echo ""
echo "  # OR install with PostgreSQL 16"
echo "  pip install packages/pgserver-postgres-16/dist/*.whl"
echo "  pip install dist/*.whl"
echo ""
echo "  # Test it"
echo "  python -c 'import pgserver; print(f\"PostgreSQL {pgserver.INSTALLED_POSTGRES_VERSION} installed\")'"
