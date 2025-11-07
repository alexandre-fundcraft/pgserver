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

### json-c (dependency for PostGIS)
JSONC_VERSION := 0.17
JSONC_TAG := json-c-$(JSONC_VERSION)-20230812
JSONC_URL := https://github.com/json-c/json-c/archive/refs/tags/$(JSONC_TAG).tar.gz
JSONC_DIR := json-c-$(JSONC_TAG)

$(JSONC_DIR).tar.gz:
	curl -L -o $(JSONC_DIR).tar.gz $(JSONC_URL)

$(JSONC_DIR)/CMakeLists.txt: $(JSONC_DIR).tar.gz
	mkdir -p $(JSONC_DIR)
	tar xzf $(JSONC_DIR).tar.gz -C $(JSONC_DIR) --strip-components=1
	touch $(JSONC_DIR)/CMakeLists.txt

$(INSTALL_PREFIX)/lib/libjson-c.so: $(JSONC_DIR)/CMakeLists.txt
	mkdir -p $(JSONC_DIR)/build
	cd $(JSONC_DIR)/build && cmake .. -DCMAKE_INSTALL_PREFIX=$(INSTALL_PREFIX) -DBUILD_SHARED_LIBS=ON
	$(MAKE) -C $(JSONC_DIR)/build -j
	$(MAKE) -C $(JSONC_DIR)/build install

.PHONY: jsonc
jsonc: $(INSTALL_PREFIX)/lib/libjson-c.so

### PROJ (dependency for PostGIS)
PROJ_VERSION := 9.3.1
PROJ_URL := https://github.com/OSGeo/PROJ/releases/download/$(PROJ_VERSION)/proj-$(PROJ_VERSION).tar.gz
PROJ_DIR := proj-$(PROJ_VERSION)

$(PROJ_DIR).tar.gz:
	curl -L -o $(PROJ_DIR).tar.gz $(PROJ_URL)

$(PROJ_DIR)/CMakeLists.txt: $(PROJ_DIR).tar.gz
	mkdir -p $(PROJ_DIR)
	tar xzf $(PROJ_DIR).tar.gz -C $(PROJ_DIR) --strip-components=1
	touch $(PROJ_DIR)/CMakeLists.txt

$(INSTALL_PREFIX)/lib/libproj.so: $(PROJ_DIR)/CMakeLists.txt
	mkdir -p $(PROJ_DIR)/build
	cd $(PROJ_DIR)/build && cmake .. -DCMAKE_INSTALL_PREFIX=$(INSTALL_PREFIX) -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=OFF
	$(MAKE) -C $(PROJ_DIR)/build -j
	$(MAKE) -C $(PROJ_DIR)/build install

.PHONY: proj
proj: $(INSTALL_PREFIX)/lib/libproj.so

### GEOS (dependency for PostGIS)
GEOS_VERSION := 3.12.1
GEOS_URL := https://github.com/libgeos/geos/releases/download/$(GEOS_VERSION)/geos-$(GEOS_VERSION).tar.bz2
GEOS_DIR := geos-$(GEOS_VERSION)

$(GEOS_DIR).tar.bz2:
	curl -L -o $(GEOS_DIR).tar.bz2 $(GEOS_URL)

$(GEOS_DIR)/CMakeLists.txt: $(GEOS_DIR).tar.bz2
	mkdir -p $(GEOS_DIR)
	tar xjf $(GEOS_DIR).tar.bz2 -C $(GEOS_DIR) --strip-components=1
	touch $(GEOS_DIR)/CMakeLists.txt

$(INSTALL_PREFIX)/lib/libgeos.so: $(GEOS_DIR)/CMakeLists.txt
	mkdir -p $(GEOS_DIR)/build
	cd $(GEOS_DIR)/build && cmake .. -DCMAKE_INSTALL_PREFIX=$(INSTALL_PREFIX) -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=OFF
	$(MAKE) -C $(GEOS_DIR)/build -j
	$(MAKE) -C $(GEOS_DIR)/build install

.PHONY: geos
geos: $(INSTALL_PREFIX)/lib/libgeos.so

### PostGIS
POSTGIS_VERSION := 3.4.2
POSTGIS_URL := https://github.com/postgis/postgis/archive/refs/tags/$(POSTGIS_VERSION).tar.gz
POSTGIS_DIR := postgis-$(POSTGIS_VERSION)

$(POSTGIS_DIR).tar.gz:
	curl -L -o $(POSTGIS_DIR).tar.gz $(POSTGIS_URL)

$(POSTGIS_DIR)/configure.ac: $(POSTGIS_DIR).tar.gz
	mkdir -p $(POSTGIS_DIR)
	tar xzf $(POSTGIS_DIR).tar.gz -C $(POSTGIS_DIR) --strip-components=1
	touch $(POSTGIS_DIR)/configure.ac

$(POSTGIS_DIR)/configure: $(POSTGIS_DIR)/configure.ac
	cd $(POSTGIS_DIR) && ./autogen.sh

$(INSTALL_PREFIX)/lib/postgis-3.so: $(POSTGIS_DIR)/configure $(INSTALL_PREFIX)/bin/postgres jsonc proj geos
	cd $(POSTGIS_DIR) && ./configure \
		--prefix=$(INSTALL_PREFIX) \
		--with-pgconfig=$(INSTALL_PREFIX)/bin/pg_config \
		--with-projdir=$(INSTALL_PREFIX) \
		--with-geosconfig=$(INSTALL_PREFIX)/bin/geos-config \
		--with-jsondir=$(INSTALL_PREFIX) \
		--without-raster \
		--without-topology
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $(MAKE) -C $(POSTGIS_DIR) -j
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $(MAKE) -C $(POSTGIS_DIR) install

.PHONY: postgis
postgis: postgres jsonc proj geos $(INSTALL_PREFIX)/lib/postgis-3.so

### other
.PHONY: clean clean-all
clean:
	rm -rf $(INSTALL_PREFIX)
	rm -rf $(POSTGRES_SRC)
	rm -rf $(POSTGRES_BLD)
	rm -rf $(PGVECTOR_DIR)
	rm -rf $(JSONC_DIR)
	rm -rf $(PROJ_DIR)
	rm -rf $(GEOS_DIR)
	rm -rf $(POSTGIS_DIR)

clean-all: clean
	rm -rf *.tar.gz *.tar.bz2