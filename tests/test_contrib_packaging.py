from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_makefile_build_target_builds_contrib():
    makefile = (REPO_ROOT / "pgbuild" / "Makefile").read_text()
    # $(POSTGRES_BLD)/src/bin/initdb/initdb target must run make -C $(POSTGRES_BLD)/contrib -j after make -C $(POSTGRES_BLD) -j
    pattern = r"\$\(MAKE\) -C \$\(POSTGRES_BLD\) -j.*?\$\(MAKE\) -C \$\(POSTGRES_BLD\)/contrib -j"
    assert re.search(pattern, makefile, re.DOTALL), "Makefile build target does not run contrib make after postgres make"

def test_makefile_install_target_installs_contrib_before_relocation():
    makefile = (REPO_ROOT / "pgbuild" / "Makefile").read_text()
    # install target must run make -C $(POSTGRES_BLD)/contrib install before the relocation loop
    install_section = makefile[makefile.find("$(INSTALL_PREFIX)/bin/postgres:") : makefile.find(".PHONY: postgres")]
    contrib_install_idx = install_section.find("$(MAKE) -C $(POSTGRES_BLD)/contrib install")
    reloc_idx = install_section.find("install_name_tool")
    assert contrib_install_idx != -1, "Makefile install target does not run contrib install"
    assert reloc_idx != -1 and contrib_install_idx < reloc_idx, "Makefile install target must install contrib before macOS relocation"

def test_version_bump_to_0_4_0():
    pyproject = (REPO_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.4.0"' in pyproject
    assert '"pgserver-postgres-17==0.4.0"' in pyproject
    assert '"pgserver-postgres-18==0.4.0"' in pyproject

    pkg17 = (REPO_ROOT / "packages" / "pgserver-postgres-17" / "pyproject.toml").read_text()
    assert 'version = "0.4.0"' in pkg17

    pkg18 = (REPO_ROOT / "packages" / "pgserver-postgres-18" / "pyproject.toml").read_text()
    assert 'version = "0.4.0"' in pkg18

def test_readme_and_changelog_documentation():
    readme = (REPO_ROOT / "README.md").read_text()
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text()

    # Documentation across README.md and CHANGELOG.md documenting standard PostgreSQL contrib extensions
    # (btree_gist, unaccent, pg_trgm, pgcrypto, etc.) are bundled alongside pgvector
    for doc in [readme, changelog]:
        for ext in ["btree_gist", "unaccent", "pg_trgm", "pgcrypto"]:
            assert ext in doc, f"{ext} not mentioned in doc"
        assert "contrib" in doc, "contrib not mentioned in doc"

    # Download URLs in README.md updated to v0.4.0
    assert "v0.3.0" not in readme, "Old v0.3.0 still present in README.md"
    assert "v0.4.0" in readme, "v0.4.0 download URLs missing in README.md"
    assert "pgserver-0.4.0-py3-none-any.whl" in readme
    assert "pgserver_postgres_18-0.4.0-py3-none-manylinux_2_17_aarch64.whl" in readme
    assert "pgserver_postgres_18-0.4.0-py3-none-macosx_11_0_arm64.whl" in readme

    # CHANGELOG.md has 0.4.0 section
    assert "## [0.4.0]" in changelog


def test_workflow_matrix_includes_linux_x86_64():
    workflow = (REPO_ROOT / ".github" / "workflows" / "build-and-test.yml").read_text()
    assert "linux-x86_64" in workflow
    assert "manylinux_2_17_x86_64" in workflow

    assert re.search(r"build_binary_wheels:.*?platform:\s*\[[^\]]*linux-x86_64[^\]]*\]", workflow, re.DOTALL)
    assert re.search(
        r"build_binary_wheels:.*?-\s*platform:\s*linux-x86_64\s*\n\s*os:\s*ubuntu-latest\s*\n\s*wheel_platform:\s*manylinux_2_17_x86_64",
        workflow,
        re.DOTALL,
    )

    assert re.search(r"test:.*?platform:\s*\[[^\]]*linux-x86_64[^\]]*\]", workflow, re.DOTALL)
    assert re.search(
        r"test:.*?-\s*platform:\s*linux-x86_64\s*\n\s*os:\s*ubuntu-latest",
        workflow,
        re.DOTALL,
    )


def test_readme_and_changelog_linux_x86_64():
    readme = (REPO_ROOT / "README.md").read_text()
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text()

    assert "Linux x86_64" in readme or "Linux x86" in readme
    assert "manylinux_2_17_x86_64" in readme
    assert "Linux x86" in changelog or "x86_64" in changelog


def test_readme_documents_pip_uv_and_poetry_installation():
    readme = (REPO_ROOT / "README.md").read_text()
    assert "pip install" in readme
    assert "[tool.uv.sources]" in readme
    assert "uv sync" in readme
    assert "[tool.poetry" in readme
