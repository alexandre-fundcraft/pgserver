#!/bin/bash
# Quick test script for local builds

set -e

VENV_DIR="test-pgserver-venv"

# Clean up any existing test environment
rm -rf "$VENV_DIR"

# Create fresh virtual environment
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install build dependencies
pip install --upgrade pip wheel

# Test PostgreSQL 18 (default)
echo ""
echo "=== Testing PostgreSQL 18 (default) ==="
pip install packages/pgserver-postgres-18/dist/*.whl
pip install dist/*.whl

python -c "
import pgserver
print(f'Installed PostgreSQL version: {pgserver.INSTALLED_POSTGRES_VERSION}')
assert pgserver.INSTALLED_POSTGRES_VERSION == 18, 'Expected PostgreSQL 18'
print('✓ PostgreSQL 18 test passed')
"

# Clean and test PostgreSQL 16
pip uninstall -y pgserver pgserver-postgres-18 pgserver-postgres-16 pgserver-postgres-17 || true

echo ""
echo "=== Testing PostgreSQL 16 ==="
pip install packages/pgserver-postgres-16/dist/*.whl
pip install dist/*.whl

python -c "
import pgserver
print(f'Installed PostgreSQL version: {pgserver.INSTALLED_POSTGRES_VERSION}')
assert pgserver.INSTALLED_POSTGRES_VERSION == 16, 'Expected PostgreSQL 16'
print('✓ PostgreSQL 16 test passed')
"

# Clean and test PostgreSQL 17
pip uninstall -y pgserver pgserver-postgres-18 pgserver-postgres-16 pgserver-postgres-17 || true

echo ""
echo "=== Testing PostgreSQL 17 ==="
pip install packages/pgserver-postgres-17/dist/*.whl
pip install dist/*.whl

python -c "
import pgserver
print(f'Installed PostgreSQL version: {pgserver.INSTALLED_POSTGRES_VERSION}')
assert pgserver.INSTALLED_POSTGRES_VERSION == 17, 'Expected PostgreSQL 17'
print('✓ PostgreSQL 17 test passed')
"

deactivate
echo ""
echo "=== All tests passed! ==="
echo "Cleaning up test environment..."
rm -rf "$VENV_DIR"
