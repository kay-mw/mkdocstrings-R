import subprocess
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

TEST_CWD = Path(__file__).parent


@pytest.mark.parametrize(
    "command",
    [
        ["mkdocs", "build", "--clean", "--strict"],
        ["zensical", "build", "--clean", "--strict"],
    ],
    ids=["mkdocs", "zensical"],
)
def test_renv_documentation_site_builds(command):
    try:
        subprocess.run(
            command, cwd=TEST_CWD, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        raise

    html = (TEST_CWD / "site" / "index.html").read_text(encoding="utf-8")
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
