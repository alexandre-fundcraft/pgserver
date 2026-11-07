import hashlib
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / ".github" / "scripts" / "build_simple_index.py"
spec = importlib.util.spec_from_file_location("build_simple_index", SCRIPT)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

PURE = "pgserver-0.4.0-py3-none-any.whl"
PLATFORM = "pgserver_postgres_17-0.4.0-py3-none-manylinux_2_17_x86_64.whl"


def run(tmp_path, names):
    wheels, site = tmp_path / "wheels", tmp_path / "site"
    wheels.mkdir()
    for name in names:
        (wheels / name).write_bytes(name.encode())
    build.main([str(wheels), str(site)])
    return site


def test_pure_wheel_listed_under_its_project(tmp_path):
    site = run(tmp_path, [PURE])
    assert PURE in (site / "simple" / "pgserver" / "index.html").read_text()


def test_project_name_is_normalized(tmp_path):
    site = run(tmp_path, [PLATFORM])
    assert PLATFORM in (site / "simple" / "pgserver-postgres-17" / "index.html").read_text()


def test_all_versions_and_platforms_on_one_page(tmp_path):
    names = [
        f"pgserver-{v}-py3-none-{p}.whl"
        for v in ("0.2.0", "0.3.0", "0.4.0")
        for p in ("macosx_11_0_arm64", "manylinux_2_17_aarch64", "manylinux_2_17_x86_64")
    ]
    page = (run(tmp_path, names) / "simple" / "pgserver" / "index.html").read_text()
    assert all(name in page for name in names)


def test_link_has_relative_href_with_sha256(tmp_path):
    page = (run(tmp_path, [PURE]) / "simple" / "pgserver" / "index.html").read_text()
    digest = hashlib.sha256(PURE.encode()).hexdigest()
    assert f'<a href="../../files/{PURE}#sha256={digest}">{PURE}</a>' in page


def test_root_index_lists_each_project_once(tmp_path):
    site = run(tmp_path, [PURE, PLATFORM, "pgserver-0.3.0-py3-none-any.whl"])
    root = (site / "simple" / "index.html").read_text()
    assert root.count('href="pgserver/"') == 1
    assert root.count('href="pgserver-postgres-17/"') == 1


def test_wheels_copied_to_files_dir(tmp_path):
    site = run(tmp_path, [PURE])
    assert (site / "files" / PURE).read_bytes() == PURE.encode()


def test_non_wheel_files_ignored(tmp_path):
    site = run(tmp_path, [PURE, "notes.txt"])
    assert not (site / "files" / "notes.txt").exists()
    assert "notes" not in (site / "simple" / "index.html").read_text()


def test_empty_input_exits_non_zero(tmp_path):
    (tmp_path / "wheels").mkdir()
    with pytest.raises(SystemExit) as exc:
        build.main([str(tmp_path / "wheels"), str(tmp_path / "site")])
    assert exc.value.code not in (0, None)
