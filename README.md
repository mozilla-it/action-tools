# `action-tools`

**action-tools** is a CLI toolkit for working with GitHub Actions and reusable workflows.

## CLI Commands

### `gendocs`

#### `action`
```
> action-tools gendocs action --help

Usage: action-tools gendocs action [OPTIONS]

  Generate README.md from GitHub Actions action.yml

Options:
  --input PATH                    Path to action.yml  [default: ./action.yml]
  --output PATH                   Path for generated README  [default:
                                  ./README.md]
  --usage-examples-dir DIRECTORY  Path to directory containing custom usage
                                  examples to include
  --help                          Show this message and exit.
```

## Setup

### Required Dependencies

Before you begin, ensure you have the following installed:

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

You can verify installation with:

```shell
uv --version
```

### Development Environment Setup

To initialize your development environment, run:

```shell
make init
```

This will:

1. Create a virtual environment in `.venv` using `uv venv`
2. Install all dependencies declared in `pyproject.toml` via `uv sync`

#### Verifying installation

After setup, confirm the CLI is working by running:

```text
action-tools --help
```

This should output the base-level usage instructions for the CLI, similar to:

```text
Usage: action-tools [OPTIONS] COMMAND [ARGS]...
...
```

#### More commands

Refer to `make help` for a summary of all available development commands, including those for for linting, formatting, and testing.