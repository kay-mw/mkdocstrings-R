# mkdocstrings-R

[![PyPI version](https://img.shields.io/pypi/v/mkdocstrings-r)](https://pypi.org/project/mkdocstrings-r/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kay-mw/mkdocstrings-R/blob/main/LICENSE)
[![Python versions](https://img.shields.io/pypi/pyversions/mkdocstrings-r)](https://pypi.org/project/mkdocstrings-r/)

An [mkdocstrings](https://mkdocstrings.github.io/) handler for R. Write your
documentation with [roxygen2](https://roxygen2.r-lib.org/) comments, and this
handler will render them into your MkDocs site.

![image](static/site_example.png)

## Installation

```bash
uv add mkdocstrings-r
```

### Requirements

- Python 3.10+
- R (accessible via `rpy2`)
- The `roxygen2` R package

`rpy2` also requires several system libraries (`zstd`, `xz`, `bzip2`, `zlib`,
`icu`). These are typically already present on most systems.

## Quick start

Given an R file at `R/math.R`:

```r
#' Add two numbers together.
#'
#' A simple function that computes the sum of two numeric inputs.
#'
#' @param x A numeric value.
#' @param y A numeric value.
#'
#' @returns A numeric value, the sum of `x` and `y`.
#'
#' @examples
#' add(1, 2)
#' add(-5, 10)
add <- function(x, y) {
  x + y
}
```

Configure your `mkdocs.yml`:

```yaml
plugins:
  - mkdocstrings:
      default_handler: R
```

Then reference the file in any Markdown page using dot-separated paths (without
the `.R` extension):

```markdown
# API Reference

::: R.math
```

Or reference the handler directly:

<!-- prettier-ignore-start -->
```markdown
# API Reference

::: R.math
    handler: R
```
<!-- prettier-ignore-end -->

This renders documentation for every function in the file, including signature,
description, parameters, return value, examples, and a collapsible source code
block.

## Supported roxygen2 tags

| Tag                    | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `@title`               | Function title (or the first line of the roxygen2 block)     |
| `@description`         | Description paragraph (or the second paragraph of the block) |
| `@details`             | Additional details section                                   |
| `@param`               | Parameter name and description                               |
| `@return` / `@returns` | Return value documentation                                   |
| `@examples`            | Example code, rendered with R syntax highlighting            |

Markdown is supported within tag descriptions (e.g., inline code, lists, links).

## Configuration

### Handler options

Configure the handler in `mkdocs.yml` under
`plugins > mkdocstrings > handlers > R`:

```yaml
plugins:
  - mkdocstrings:
      default_handler: R
      handlers:
        R:
          lib_loc: "/path/to/R/library"
```

#### `lib_loc`

Path to the R library directory containing `roxygen2`. This is only needed if
`rpy2` can't auto-detect your library location — for example, when using `renv`
and the `renv/` folder isn't in the directory where you're running `mkdocs`.

To find your library paths, run `.libPaths()` in an R console.

## How it works

1. The handler converts your dot-separated identifier (e.g., `R.math`) to a file
   path (`R/math.R`)
2. It calls `roxygen2::parse_file()` via `rpy2` to parse the roxygen2 comments
3. The parsed tags are mapped to a structured data model
4. A Jinja template renders the data as HTML within your MkDocs site
