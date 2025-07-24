import pathlib
import re
import subprocess
from typing import Any, Optional

import click
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

from .models import ActionInput, GitHubAction

GITHUB_REMOTE_REGEX = re.compile(r"github\.com[:/](?P<org_repo>[^/\s.]+/[^/\s.]+)")


def list_git_remotes(git_root: pathlib.Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(git_root), "remote", "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"`git -C {str(git_root)} remote -v`: {e.stderr.strip()}")

    return result.stdout


def get_action_path(input_path: pathlib.Path) -> str:
    """Return GitHub 'org/repo[/subdir]' for an action's path inside a Git repo with at least one Github remote"""

    # Walk up to find the first .git directory
    git_root = None
    for directory in input_path.parents:
        if (directory / ".git").exists():
            git_root = directory.resolve()
            break
    if not git_root:
        raise FileNotFoundError("No .git directory found in any parent directories.")

    org_repo = None
    for line in list_git_remotes(git_root).splitlines():
        if match := GITHUB_REMOTE_REGEX.search(line):
            org_repo = match.group("org_repo")
            break
    if not org_repo:
        raise ValueError("No GitHub remote found.")

    # Compute relative path from repo root to directory containing action
    rel_path = input_path.resolve().parent.relative_to(git_root)
    return f"{org_repo}/{rel_path}".rstrip("/.")


def format_usage_lines(inputs: dict[str, ActionInput]):
    for key, spec in inputs.items():
        value = str(spec.example if spec.required else spec.default)
        if "\n" in value:
            yield f"    {key}: |"
            yield from (f"      {line}" for line in value.splitlines())
        else:
            yield f"    {key}: {value}"


def generate_example_usage(action_path: str, inputs: dict[str, ActionInput]) -> str:
    input_usage = [
        "```yaml",
        f"- uses: {action_path}",
        "  with:",
        *format_usage_lines(inputs),
        "```",
    ]
    return "\n".join(input_usage)


def load_custom_usage_examples(usage_examples_dir: pathlib.Path) -> str:
    if not usage_examples_dir.is_dir():
        raise ValueError(f"Usage dir '{usage_examples_dir}' does not exist")

    usage_files = sorted(usage_examples_dir.glob("*.md"))
    examples = []

    for file_path in usage_files:
        content = file_path.read_text().strip()
        if content:
            examples.append(content)

    return "\n\n".join(examples)


def generate_minimal_usage_example(
    action_path: str, inputs: dict[str, ActionInput]
) -> str:
    inputs = {key: spec for key, spec in inputs.items() if spec.required}
    return generate_example_usage(action_path, inputs)


def generate_defaults_usage_example(action_path: str, inputs: dict[str, Any]) -> str:
    inputs = {
        key: spec for key, spec in inputs.items() if spec.required or spec.default
    }
    return generate_example_usage(action_path, inputs)


# =============================================================================
# Main Action README generator
# =============================================================================
def generate_action_docs(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    usage_examples_dir: Optional[pathlib.Path] = None,
) -> None:
    yaml = YAML()
    data = yaml.load(input_path.read_text())
    action = GitHubAction(**data)
    # get inputs and generate example usage
    action_path = get_action_path(input_path)
    minimal_usage_example = generate_minimal_usage_example(action_path, action.inputs)
    defaults_usage_example = generate_defaults_usage_example(action_path, action.inputs)

    # load custom usage examples
    custom_usage_examples = None
    if usage_examples_dir:
        custom_usage_examples = load_custom_usage_examples(usage_examples_dir)

    # build template and write out README
    env = Environment(loader=FileSystemLoader("src/action_tools/templates"))
    template = env.get_template("action_readme.md.jinja2")
    output = template.render(
        name=action.name,
        description=action.description,
        inputs=action.inputs,
        outputs=action.outputs,
        minimal_usage_example=minimal_usage_example,
        defaults_usage_example=defaults_usage_example,
        custom_usage_examples=custom_usage_examples,
    )
    output_path.write_text(output)


# =============================================================================
# CLI Commands
# =============================================================================
@click.group()
def gendocs():
    """Generate documentation artifacts for GitHub Actions components."""
    pass


@gendocs.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(path_type=pathlib.Path, exists=True, readable=True),
    default="./action.yml",
    show_default=True,
    help="Path to action.yml",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=pathlib.Path, writable=True),
    default="./README.md",
    show_default=True,
    help="Path for generated README",
)
@click.option(
    "--usage-examples-dir",
    type=click.Path(path_type=pathlib.Path, exists=True, file_okay=False),
    required=False,
    help="Path to directory containing custom usage examples to include",
)
def action(
    input_path,
    output_path,
    usage_examples_dir,
):
    """Generate README.md from GitHub Actions action.yml"""

    generate_action_docs(
        input_path=input_path,
        output_path=output_path,
        usage_examples_dir=usage_examples_dir,
    )
