# PostGIS Support in pgserver

This document describes the PostGIS spatial database extension support added to pgserver.

## Overview

PostGIS extends PostgreSQL to support geographic objects, allowing location queries to be run in SQL. pgserver now includes PostGIS 3.4.2 along with all its required dependencies.

## Dependencies

PostGIS requires several libraries to function:

- **JSON-C 0.17** - JSON support for GeoJSON and other JSON-based operations
- **PROJ 9.3.1** - Cartographic projections library for coordinate transformations
- **GEOS 3.12.1** - Geometry Engine Open Source for geometric operations
- **PostGIS 3.4.2** - The spatial database extension itself

All dependencies are built from source and bundled with the pgserver package.

## Build Configuration

The PostGIS build is configured with:
- `--without-raster` - Raster support disabled to reduce dependencies
- `--without-topology` - Topology support disabled to reduce dependencies

These features can be enabled if needed by modifying the PostGIS configure flags in `pgbuild/Makefile`.

## Usage

To use PostGIS in your pgserver application:

```python
import pgserver

db = pgserver.get_server(MY_PGDATA)
# Create the PostGIS extension
db.psql('CREATE EXTENSION postgis;')

# Now you can use PostGIS functions
db.psql("""
    CREATE TABLE locations (
        id SERIAL PRIMARY KEY,
        name TEXT,
        geom GEOMETRY(Point, 4326)
    );
""")

db.psql("""
    INSERT INTO locations (name, geom)
    VALUES ('San Francisco', ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326));
""")

# Query spatial data
result = db.psql("SELECT name, ST_AsText(geom) FROM locations;")
print(result)
```

## Testing

The test suite includes a comprehensive PostGIS test that verifies:
1. Extension creation
2. PostGIS version detection
3. Creating tables with geometry columns
4. Inserting spatial data
5. Querying spatial data

Run the tests with:
```bash
pytest tests/test_pgserver.py::test_postgis -v
```

## Build Requirements

Building pgserver with PostGIS requires:
- CMake 3.x+
- autoconf
- automake
- libtool
- pkg-config
- Standard C/C++ build tools (gcc/g++ or clang)

## File Changes

The following files were modified to add PostGIS support:

1. **pgbuild/Makefile** - Added build targets for JSON-C, PROJ, GEOS, and PostGIS
2. **README.md** - Updated documentation to mention PostGIS support
3. **tests/test_pgserver.py** - Added comprehensive PostGIS test
4. **POSTGIS.md** - This documentation file

## Build Process

The build process follows this order:

1. PostgreSQL 16.2
2. pgvector 0.6.2
3. JSON-C 0.17
4. PROJ 9.3.1
5. GEOS 3.12.1
6. PostGIS 3.4.2

Each component is built and installed to the `src/pgserver/pginstall/` directory.

## Version Compatibility

- PostgreSQL: 16.2
- PostGIS: 3.4.2 (compatible with PostgreSQL 16)
- PROJ: 9.3.1
- GEOS: 3.12.1
- JSON-C: 0.17

These versions are tested together and known to be compatible.

## Platform Support

PostGIS support is available on all platforms supported by pgserver:
- Linux (manylinux)
- macOS (Intel and Apple Silicon)
- Windows

The GitHub Actions CI/CD pipeline builds and tests PostGIS on all platforms.

## Resources

- [PostGIS Official Documentation](https://postgis.net/documentation/)
- [PostGIS GitHub Repository](https://github.com/postgis/postgis)
- [PROJ Documentation](https://proj.org/)
- [GEOS Documentation](https://libgeos.org/)
