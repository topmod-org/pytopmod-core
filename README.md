# PyTopMod - Core

This is a Python implementation of the core data structures and algorithms involved in TopMod & TopMod4D.

The goal of this repository is to provide a flexible environment for experimentation and testing, therefore we optimize for readability and clarity over conciseness and performance.

## Repository Structure

We follow the [Python package `src` layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/#), i.e the code that is meant to be importable is located under a `src` subddirectory. Note that in order to run the scripts under `scripts`, the project has to be installed (see [Editable Installation](#editable-installation) section below).

From the repository root, do:

```
pip install --editable .
```

Note that we recommend using a virtual environment (see [Virtual Environment](#virtual-environment) section below).

## Style

We generally follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), with some exceptions.

### Formatting

In order to prevent style-related discussions, we use the [`black`](https://black.readthedocs.io/en/stable/) formatter for all `.py` files. Black is an opinionated formatter and therefore some of its enforced rules collide with the general style guide mentioned above, in particular:

- We use PEP8 standard 4-spaces indentation.
- Max line length is set to 88 instead of 80.

### Linting

We use [`flake8`](https://flake8.pycqa.org/en/6.1.0/index.html) for linting. There are two collisions with the `black` formatter which are mitigated by configuring `flake8` in `setup.cfg` (see [documentation](https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#flake8)).

### Type checking

We use [`mypy`](https://mypy.readthedocs.io/en/stable/) for strict type checking.

### Imports sorting

We use [`isort`](https://pycqa.github.io/isort/) to sort import statements. Compatibility with the `black` formatter is ensured by setting `profile = black` in `isort`'s settings in `setup.cfg` (see [documentation](https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#isort)).

## Workspace configuration

### Virtual Environment

We recommend using a [virtual environment](https://docs.python.org/3/library/venv.html).

In the root of the repository, do:

```
python3 -m venv .venv
source ./venv/bin/activate
```

> [!NOTE]
> VSCode will automatically pick up virtual environments created in a `.venv` directory.

### Dev Dependencies

Install dev dependencies:

```
pip install -r requirements_dev.txt
```

This will install the various formatting, linting and type checking tools mentioned in the section above (`black`, `flake8`, `isort`, `mypy`).

### Editable Installation

Install the pytopmod package as [_editable installation_](https://setuptools.pypa.io/en/latest/userguide/development_mode.html):

```
pip install --editable .
```

### Misc.

> [!NOTE]
> We provide repository-specific settings for VSCode in the `.vscode` directory. In addition to these settings we recommend using the following (e.g in VSCode user settings JSON file):

```json
"[python]": {
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  },
}
```
