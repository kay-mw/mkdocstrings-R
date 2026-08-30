import os
import shutil
import subprocess
from inspect import cleandoc
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

TEST_CWD = Path(__file__).parent

BUILD_COMMANDS = [
    ["mkdocs", "build", "--clean", "--strict"],
    ["zensical", "build", "--clean", "--strict"],
]
IDS = ["mkdocs", "zensical"]


def run_command(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, check=False
    )

    if result.returncode != 0:
        pytest.fail(
            f"Command failed: {' '.join(command)}\n\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}",
            pytrace=False,
        )

    return result


def assert_rendered_site(site_dir: Path) -> None:
    html = (site_dir / "index.html").read_text(encoding="utf-8")
    page = BeautifulSoup(html, "html.parser")

    assert page.select_one("h2#add") is not None
    assert page.select_one("h2#subtract") is not None

    text = page.get_text("", strip=True)

    # Function signature
    assert "add<-function(x,y)" in text
    assert "subtract<-function(x,y)" in text

    # Description
    assert "A simple function that computes the sum of two numeric inputs." in text
    assert "A simple function that subtracts two numeric inputs." in text

    assert "Parameters:" in text
    assert "Returns:" in text

    # Source
    assert "Source code" in text
    assert "R/main.R" in text


@pytest.mark.parametrize("command", BUILD_COMMANDS, ids=IDS)
def test_renv_documentation_site_builds(command):
    run_command(command, cwd=TEST_CWD)
    assert_rendered_site(TEST_CWD / "site")


@pytest.mark.parametrize("command", BUILD_COMMANDS, ids=IDS)
def test_lib_paths_option(command, tmp_path: Path):
    result = run_command(["Rscript", "-e", "cat(renv::paths$library())"], cwd=TEST_CWD)
    lib_loc = result.stdout.strip()

    mkdocs_yml = cleandoc(f"""
    site_name: My Docs

    theme:
      name: material

    plugins:
      - mkdocstrings:
          default_handler: R
          handlers:
            R:
              lib_loc: {lib_loc}
    """)

    index_md = cleandoc("""
    # R Handler

    ::: R.main
    """)

    (tmp_path / "mkdocs.yml").write_text(mkdocs_yml, encoding="utf-8")

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text(index_md, encoding="utf-8")

    (tmp_path / "R").mkdir()
    shutil.copy(src=TEST_CWD / "R" / "main.R", dst=tmp_path / "R" / "main.R")

    env = os.environ.copy()

    for var in ("R_LIBS", "R_LIBS_USER", "R_LIBS_SITE"):
        env.pop(var, None)

    run_command(command, cwd=tmp_path, env=env)
    assert_rendered_site(tmp_path / "site")
