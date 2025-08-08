from unittest.mock import MagicMock

import pytest

from action_tools import github
from action_tools import usage as usage_module
from action_tools.models import Action, Workflow
from action_tools.usage import classify_target, find_usage, validate_exists


@pytest.fixture
def mock_github_client():
    return MagicMock(spec=github.Client)


# ---------- classify_target ----------


@pytest.mark.parametrize(
    "version",
    (
        [
            "",
            "@v1",
            "@v1.2.3",
            "@54a43938e6d916589114e065d055a5d42c131e70",
        ]
    ),
)
@pytest.mark.parametrize(
    "extension",
    [".yaml", ".yml"],
)
def test_classify_target_workflow(extension, version):
    target = f"my-org/my-repo/.github/workflows/build{extension}{version}"
    result = classify_target(target)
    assert isinstance(result, Workflow)
    assert result.org == "my-org"
    assert result.repo == "my-repo"
    assert result.subpath == f"/.github/workflows/build{extension}"


@pytest.mark.parametrize(
    "subpath",
    (
        [
            "",
            "/action-dir",
        ]
    ),
)
@pytest.mark.parametrize(
    "version",
    (
        [
            "",
            "@v1",
            "@v1.2.3",
            "@54a43938e6d916589114e065d055a5d42c131e70",
        ]
    ),
)
def test_classify_target_action(version, subpath):
    target = f"my-org/my-repo{subpath}{version}"
    result = classify_target(target)
    assert isinstance(result, Action)
    assert result.org == "my-org"
    assert result.repo == "my-repo"
    assert result.subpath == subpath


def test_classify_target_invalid():
    target = "invalid-target"
    with pytest.raises(ValueError, match=f"target {target} does not appear"):
        classify_target("invalid-target")


# ---------- validate_exists ----------


def test_validate_exists_workflow_true(mock_github_client):
    resource = Workflow(
        org="my-org", repo="my-repo", subpath="/.github/workflows/build.yml"
    )
    mock_github_client.get_repo_contents.return_value = [{"name": "build.yml"}]

    assert validate_exists(resource, mock_github_client)


def test_validate_exists_action_true(mock_github_client):
    resource = Action(org="org", repo="repo", subpath="/some-action")
    mock_github_client.get_repo_contents.return_value = [{"name": "action.yml"}]

    assert validate_exists(resource, mock_github_client)


def test_validate_exists_action_false(mock_github_client):
    resource = Action(org="org", repo="repo", subpath="/some-action")
    mock_github_client.get_repo_contents.return_value = [{"name": "other.yml"}]

    assert not validate_exists(resource, mock_github_client)


def test_validate_exists_not_found(mock_github_client):
    resource = Action(org="org", repo="repo", subpath="/nope")
    mock_github_client.get_repo_contents.side_effect = (
        usage_module.github.ClientStatusError(
            "Not Found", status_code=404, request=None, response=None
        )
    )

    assert not validate_exists(resource, mock_github_client)


def test_validate_exists_another_status_error(mock_github_client):
    resource = Action(org="org", repo="repo", subpath="/nope")
    mock_github_client.get_repo_contents.side_effect = (
        usage_module.github.ClientStatusError(
            "Gulp.", status_code=500, request=None, response=None
        )
    )

    with pytest.raises(github.ClientStatusError):
        validate_exists(resource, mock_github_client)


# ---------- find_usage ----------


def test_find_usage_returns_sorted_repos(mock_github_client):
    mock_github_client.search_code.return_value = [
        {"repository": {"full_name": "z-org/z-repo"}},
        {"repository": {"full_name": "a-org/a-repo"}},
    ]

    repos = find_usage("my-org/my-repo/path", mock_github_client)
    assert repos == ["a-org/a-repo", "z-org/z-repo"]


def test_find_usage_returns_no_usage(mock_github_client):
    mock_github_client.search_code.return_value = []

    repos = find_usage("my-org/my-repo/path", mock_github_client)
    assert repos == []
