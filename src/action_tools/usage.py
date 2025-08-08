import re
from typing import Optional

import click

from . import github
from .models import Action, Resource, Workflow

WORKFLOW_REGEX = re.compile(
    r"^(?P<org>[\w.-]+)/(?P<repo>[\w.-]+)(?P<subpath>/\.github/workflows/.+\.(yaml|yml))(?:@.+)?$"
)


ACTION_REGEX = re.compile(
    r"^(?P<org>[\w.-]+)/(?P<repo>[\w.-]+)(?P<subpath>(?:/[\w.-]+)*)(?:@.+)?$"
)


def classify_target(target: str) -> Resource:
    if match := WORKFLOW_REGEX.match(target):
        return Workflow(
            org=match.group("org"),
            repo=match.group("repo"),
            subpath=match.group("subpath"),
        )
    if match := ACTION_REGEX.match(target):
        return Action(
            org=match.group("org"),
            repo=match.group("repo"),
            subpath=match.group("subpath"),
        )
    raise ValueError(f"target {target} does not appear to be an action or workflow")


def validate_exists(resource: Resource, client: github.Client) -> bool:
    try:
        contents = client.get_repo_contents(
            org=resource.org, repo=resource.repo, subpath=resource.subpath
        )
    except github.ClientStatusError as exc:
        if exc.status_code == 404:
            return False

    if isinstance(resource, Workflow):
        return bool(contents)
    elif isinstance(resource, Action):
        return any(file["name"] in {"action.yml", "action.yaml"} for file in contents)
    else:
        raise ValueError(
            f"Unsupported resource type or invalid path: expected a workflow or action at "
            f"{resource.org}/{resource.repo}/{resource.subpath}, but none was found. "
            "Ensure the path exists in the repository and contains a valid GitHub Action "
            "(with 'action.yml' or 'action.yaml') or a workflow file."
        )


def find_usage(target: str, client: github.Client):
    query = f'"uses: {target}" language:YAML'
    items = client.search_code(query)
    repos = {item["repository"]["full_name"] for item in items}
    return sorted(repos)


def _usage(target: str, token: str, client: Optional[github.Client] = None):
    if not client:
        client = github.Client(token=token)

    target, *_ = target.partition("@")
    resource = classify_target(target)
    if not validate_exists(resource, client):
        raise click.ClickException(f"Could not find {target}")
    repos = find_usage(target, client)
    click.echo("\n".join(repos))


@click.command(
    epilog="""\b
    Example Usage:
      action-tools usage "my-org/my-repo/.github/workflows/build.yml"
      action-tools usage "my-org/my-action/action-dir"
      action-tools usage "my-org/my-action@v1.2.3"
    
    \b
    Example Output:
      some-org/some-repo
      some-org/another-repo
    """
)
@click.argument("target", type=str)
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub token for authentication")
def usage(target, token):
    """Search GitHub for repositories that reference a reusable workflow or action.

    TARGET must be a reference to a GitHub Action or reusable workflow as would be specified in a job or step's `uses` directive.
    """
    return _usage(target, token)
