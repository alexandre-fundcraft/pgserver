SHELL := /bin/bash
INSTALL_PREFIX := $(shell pwd)/../src/pgserver/pginstall/
BUILD := $(shell pwd)/pgbuild/

.PHONY: all
all: pgvector postgis postgres

### postgres
POSTGRES_VERSION := 16.2
POSTGRES_URL := https://ftp.postgresql.org/pub/source/v$(POSTGRES_VERSION)/postgresql-$(POSTGRES_VERSION).tar.gz
POSTGRES_SRC := postgresql-$(POSTGRES_VERSION)
POSTGRES_BLD := $(POSTGRES_SRC)

$(POSTGRES_SRC).tar.gz:
	curl -L -O $(POSTGRES_URL)

## extract
$(POSTGRES_SRC)/configure: $(POSTGRES_SRC).tar.gz
	tar xzf $(POSTGRES_SRC).tar.gz
	touch $(POSTGRES_SRC)/configure

## configure
$(POSTGRES_BLD)/config.status: $(POSTGRES_SRC)/configure
	mkdir -p $(POSTGRES_BLD)
	cd $(POSTGRES_BLD) && ../$(POSTGRES_SRC)/configure --prefix=$(INSTALL_PREFIX) --without-readline --without-icu

## build
# https://stackoverflow.com/questions/68379786/
# for explanation of unsetting make env variables prior to calling postgres' own make
$(POSTGRES_BLD)/src/bin/initdb/initdb: $(POSTGRES_BLD)/config.status
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $(MAKE) -C $(POSTGRES_BLD) -j

## install to INSTALL_PREFIX
$(INSTALL_PREFIX)/bin/postgres: $(POSTGRES_BLD)/config.status
	mkdir -p $(INSTALL_PREFIX)
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $(MAKE) -C $(POSTGRES_BLD) install

.PHONY: postgres
postgres: $(INSTALL_PREFIX)/bin/postgres

### pgvector
PGVECTOR_TAG := v0.6.2
PGVECTOR_URL := https://github.com/pgvector/pgvector/archive/refs/tags/$(PGVECTOR_TAG).tar.gz
PGVECTOR_DIR := pgvector-$(PGVECTOR_TAG)

$(PGVECTOR_DIR).tar.gz:
	curl -L -o $(PGVECTOR_DIR).tar.gz $(PGVECTOR_URL)

$(PGVECTOR_DIR)/Makefile: $(PGVECTOR_DIR).tar.gz
	# tar extract into pgvector-$(PGVECTOR_TAG)
	mkdir -p $(PGVECTOR_DIR)
	tar xzf $(PGVECTOR_DIR).tar.gz -C $(PGVECTOR_DIR) --strip-components=1
	touch $(PGVECTOR_DIR)/Makefile

$(INSTALL_PREFIX)/lib/vector.so: $(PGVECTOR_DIR)/Makefile $(INSTALL_PREFIX)/bin/postgres
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS \
		&& export PG_CONFIG=$(INSTALL_PREFIX)/bin/pg_config \
		&& $(MAKE) -C $(PGVECTOR_DIR) -j \
		&& $(MAKE) -C $(PGVECTOR_DIR) install

.PHONY: pgvector
pgvector: postgres $(INSTALL_PREFIX)/lib/vector.so

### PostGIS dependencies and extension
CMAKE_FLAGS := -DCMAKE_INSTALL_PREFIX=$(INSTALL_PREFIX) -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=OFF

# JSON-C 0.18
JSONC_VER := 0.18
JSONC_TAG := json-c-$(JSONC_VER)-20240915
$(JSONC_TAG).tar.gz:
	curl -L -o $@ https://github.com/json-c/json-c/archive/refs/tags/$(JSONC_TAG).tar.gz
$(JSONC_TAG)/CMakeLists.txt: $(JSONC_TAG).tar.gz
	mkdir -p $(JSONC_TAG) && tar xzf $< -C $(JSONC_TAG) --strip-components=1 && touch $@
$(INSTALL_PREFIX)/lib/libjson-c.so: $(JSONC_TAG)/CMakeLists.txt
	@echo "======== Building JSON-C $(JSONC_VER) ========"
	mkdir -p $(JSONC_TAG)/build && cd $(JSONC_TAG)/build && cmake .. $(CMAKE_FLAGS) -DBUILD_APPS=OFF && $(MAKE) -j && $(MAKE) install
	@echo "======== JSON-C build complete ========"

# PROJ 9.7.0
PROJ_VER := 9.7.0
proj-$(PROJ_VER).tar.gz:
	curl -L -o $@ https://github.com/OSGeo/PROJ/releases/download/$(PROJ_VER)/proj-$(PROJ_VER).tar.gz
proj-$(PROJ_VER)/CMakeLists.txt: proj-$(PROJ_VER).tar.gz
	mkdir -p proj-$(PROJ_VER) && tar xzf $< -C proj-$(PROJ_VER) --strip-components=1 && touch $@
$(INSTALL_PREFIX)/lib/libproj.so: proj-$(PROJ_VER)/CMakeLists.txt
	@echo "======== Building PROJ $(PROJ_VER) (this may take 5-10 minutes) ========"
	mkdir -p proj-$(PROJ_VER)/build && cd proj-$(PROJ_VER)/build && cmake .. $(CMAKE_FLAGS) -DBUILD_APPS=OFF -DENABLE_TIFF=OFF -DENABLE_CURL=OFF && $(MAKE) -j && $(MAKE) install
	@echo "======== PROJ build complete ========"

# GEOS 3.14.1
GEOS_VER := 3.14.1
geos-$(GEOS_VER).tar.bz2:
	curl -L -o $@ https://github.com/libgeos/geos/releases/download/$(GEOS_VER)/geos-$(GEOS_VER).tar.bz2
geos-$(GEOS_VER)/CMakeLists.txt: geos-$(GEOS_VER).tar.bz2
	mkdir -p geos-$(GEOS_VER) && tar xjf $< -C geos-$(GEOS_VER) --strip-components=1 && touch $@
$(INSTALL_PREFIX)/lib/libgeos.so: geos-$(GEOS_VER)/CMakeLists.txt
	@echo "======== Building GEOS $(GEOS_VER) (this may take 10-15 minutes) ========"
	mkdir -p geos-$(GEOS_VER)/build && cd geos-$(GEOS_VER)/build && cmake .. $(CMAKE_FLAGS) && $(MAKE) -j && $(MAKE) install
	@echo "======== GEOS build complete ========"

# PostGIS 3.6.0
POSTGIS_VER := 3.6.0
postgis-$(POSTGIS_VER).tar.gz:
	curl -L -o $@ https://github.com/postgis/postgis/archive/refs/tags/$(POSTGIS_VER).tar.gz
postgis-$(POSTGIS_VER)/configure.ac: postgis-$(POSTGIS_VER).tar.gz
	mkdir -p postgis-$(POSTGIS_VER) && tar xzf $< -C postgis-$(POSTGIS_VER) --strip-components=1 && touch $@
postgis-$(POSTGIS_VER)/configure: postgis-$(POSTGIS_VER)/configure.ac
	cd postgis-$(POSTGIS_VER) && ./autogen.sh
$(INSTALL_PREFIX)/lib/postgis-3.so: postgis-$(POSTGIS_VER)/configure $(INSTALL_PREFIX)/bin/postgres $(INSTALL_PREFIX)/lib/libjson-c.so $(INSTALL_PREFIX)/lib/libproj.so $(INSTALL_PREFIX)/lib/libgeos.so
	@echo "======== Configuring PostGIS $(POSTGIS_VER) ========"
	cd postgis-$(POSTGIS_VER) && ./configure --prefix=$(INSTALL_PREFIX) --with-pgconfig=$(INSTALL_PREFIX)/bin/pg_config \
		--with-projdir=$(INSTALL_PREFIX) --with-geosconfig=$(INSTALL_PREFIX)/bin/geos-config --with-jsondir=$(INSTALL_PREFIX) \
		--without-raster --without-topology
	@echo "======== Building PostGIS $(POSTGIS_VER) ========"
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $(MAKE) -C postgis-$(POSTGIS_VER) -j && $(MAKE) -C postgis-$(POSTGIS_VER) install
	@echo "======== PostGIS build complete ========"

.PHONY: postgis
postgis: $(INSTALL_PREFIX)/lib/postgis-3.so

### other
.PHONY: clean clean-all
clean:
	rm -rf $(INSTALL_PREFIX) $(POSTGRES_SRC) $(POSTGRES_BLD) $(PGVECTOR_DIR)
	rm -rf $(JSONC_TAG) proj-$(PROJ_VER) geos-$(GEOS_VER) postgis-$(POSTGIS_VER)

clean-all: clean
	rm -rf *.tar.gz *.tar.bz2