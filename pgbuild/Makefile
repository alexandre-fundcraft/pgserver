SHELL := /bin/bash
INSTALL_PREFIX_BASE := $(shell pwd)/../src/pgserver/pginstall/
BUILD := $(shell pwd)/pgbuild/

.PHONY: all
all: postgres-all pgvector-all

### PostgreSQL version definitions
PG16_VERSION := 16.10
PG17_VERSION := 17.6
PG18_VERSION := 18.0

# Template for building a specific PostgreSQL version
# Args: $(1) = version number (e.g., 16.10), $(2) = major version (e.g., 16)
define POSTGRES_TEMPLATE

POSTGRES_$(2)_URL := https://ftp.postgresql.org/pub/source/v$(1)/postgresql-$(1).tar.gz
POSTGRES_$(2)_SRC := postgresql-$(1)
POSTGRES_$(2)_BLD := postgresql-$(1)
POSTGRES_$(2)_INSTALL := $(INSTALL_PREFIX_BASE)pg$(2)/

$$(POSTGRES_$(2)_SRC).tar.gz:
	curl -L -O $$(POSTGRES_$(2)_URL)

$$(POSTGRES_$(2)_SRC)/configure: $$(POSTGRES_$(2)_SRC).tar.gz
	tar xzf $$(POSTGRES_$(2)_SRC).tar.gz
	touch $$(POSTGRES_$(2)_SRC)/configure

$$(POSTGRES_$(2)_BLD)/config.status: $$(POSTGRES_$(2)_SRC)/configure
	mkdir -p $$(POSTGRES_$(2)_BLD)
	cd $$(POSTGRES_$(2)_BLD) && ../$$(POSTGRES_$(2)_SRC)/configure --prefix=$$(POSTGRES_$(2)_INSTALL) --without-readline --without-icu

$$(POSTGRES_$(2)_BLD)/src/bin/initdb/initdb: $$(POSTGRES_$(2)_BLD)/config.status
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $$(MAKE) -C $$(POSTGRES_$(2)_BLD) -j

$$(POSTGRES_$(2)_INSTALL)bin/postgres: $$(POSTGRES_$(2)_BLD)/config.status
	mkdir -p $$(POSTGRES_$(2)_INSTALL)
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS && $$(MAKE) -C $$(POSTGRES_$(2)_BLD) install

.PHONY: postgres-$(2)
postgres-$(2): $$(POSTGRES_$(2)_INSTALL)bin/postgres

endef

# Generate rules for each PostgreSQL version
$(eval $(call POSTGRES_TEMPLATE,$(PG16_VERSION),16))
$(eval $(call POSTGRES_TEMPLATE,$(PG17_VERSION),17))
$(eval $(call POSTGRES_TEMPLATE,$(PG18_VERSION),18))

.PHONY: postgres-all
postgres-all: postgres-16 postgres-17 postgres-18

### pgvector
PGVECTOR_TAG := v0.8.0
PGVECTOR_URL := https://github.com/pgvector/pgvector/archive/refs/tags/$(PGVECTOR_TAG).tar.gz
PGVECTOR_DIR := pgvector-$(PGVECTOR_TAG)

$(PGVECTOR_DIR).tar.gz:
	curl -L -o $(PGVECTOR_DIR).tar.gz $(PGVECTOR_URL)

$(PGVECTOR_DIR)/Makefile: $(PGVECTOR_DIR).tar.gz
	mkdir -p $(PGVECTOR_DIR)
	tar xzf $(PGVECTOR_DIR).tar.gz -C $(PGVECTOR_DIR) --strip-components=1
	touch $(PGVECTOR_DIR)/Makefile

# Template for building pgvector for a specific PostgreSQL version
# Args: $(1) = major version (e.g., 16)
define PGVECTOR_TEMPLATE

PGVECTOR_$(1)_DIR := pgvector-$(1)

$$(PGVECTOR_$(1)_DIR)/Makefile: $$(PGVECTOR_DIR)/Makefile
	rm -rf $$(PGVECTOR_$(1)_DIR)
	cp -r $$(PGVECTOR_DIR) $$(PGVECTOR_$(1)_DIR)

$$(INSTALL_PREFIX_BASE)pg$(1)/lib/vector.so: $$(PGVECTOR_$(1)_DIR)/Makefile $$(INSTALL_PREFIX_BASE)pg$(1)/bin/postgres
	unset MAKELEVEL && unset MAKEFLAGS && unset MFLAGS \
		&& export PG_CONFIG=$$(INSTALL_PREFIX_BASE)pg$(1)/bin/pg_config \
		&& $$(MAKE) -C $$(PGVECTOR_$(1)_DIR) clean \
		&& $$(MAKE) -C $$(PGVECTOR_$(1)_DIR) -j \
		&& $$(MAKE) -C $$(PGVECTOR_$(1)_DIR) install

.PHONY: pgvector-$(1)
pgvector-$(1): postgres-$(1) $$(INSTALL_PREFIX_BASE)pg$(1)/lib/vector.so

endef

# Generate rules for pgvector for each PostgreSQL version
$(eval $(call PGVECTOR_TEMPLATE,16))
$(eval $(call PGVECTOR_TEMPLATE,17))
$(eval $(call PGVECTOR_TEMPLATE,18))

.PHONY: pgvector-all
pgvector-all: pgvector-16 pgvector-17 pgvector-18

### other
.PHONY: clean clean-all
clean:
	rm -rf $(INSTALL_PREFIX_BASE)
	rm -rf postgresql-*
	rm -rf pgvector-*

clean-all: clean
	rm -rf *.tar.gz