import pathlib
import shutil

import pytest

from action_tools.gendocs import generate_action_docs, get_action_path


@pytest.fixture
def _base_git_repo(tmp_path):
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture
def action_yml_root(_base_git_repo):
    path = _base_git_repo / "action.yml"
    path.write_text("Fake action.yml at the root")
    return path


@pytest.fixture
def action_yml_subdir(_base_git_repo):
    subdir = _base_git_repo / "subdir"
    subdir.mkdir()
    path = subdir / "action.yml"
    path.write_text("Fake action.yml in a subdirectory")
    return path


@pytest.fixture
def remote_no_origin(mocker):
    mocker.patch("action_tools.gendocs.list_git_remotes", return_value="")


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        ("git@github.com:org/repo.git", "org/repo"),
        ("https://github.com/org/repo.git", "org/repo"),
        ("git@github.com:org/repo", "org/repo"),
        ("https://github.com/org/repo", "org/repo"),
        ("git@github.com:some-org/some_repo", "some-org/some_repo"),
        ("https://github.com/some-org/some_repo", "some-org/some_repo"),
    ],
)
def test_get_action_path_at_root(action_yml_root, mocker, remote, expected):
    mocker.patch(
        "action_tools.gendocs.list_git_remotes",
        return_value=f"origin\t{remote} (fetch)\n",
    )

    result = get_action_path(action_yml_root)
    assert result == expected


def test_get_action_path_in_subdir(action_yml_subdir, mocker):
    mocker.patch(
        "action_tools.gendocs.list_git_remotes",
        return_value="origin\tgit@github.com:org/repo.git (fetch)\n",
    )

    result = get_action_path(action_yml_subdir)
    assert result == "org/repo/subdir"


def test_multiple_origins(action_yml_root, mocker):
    remotes = "origin\tgit@github.com:org/repo.git (fetch)"
    "otherorigin\tgit@github.com:other/org.git (fetch)"

    mocker.patch("action_tools.gendocs.list_git_remotes", return_value=remotes)
    result = get_action_path(action_yml_root)
    assert result == "org/repo"


def test_no_origin(action_yml_root, remote_no_origin):
    with pytest.raises(ValueError, match="No GitHub remote found."):
        get_action_path(action_yml_root)


def test_generate_action_docs_basic(tmp_path, mocker):
    (tmp_path / ".git").mkdir()
    input_path = pathlib.Path("tests/gendocs/__fixtures__/action.yml")
    shutil.copy(input_path, tmp_path)

    output_path = tmp_path / "README.md"

    mocker.patch(
        "action_tools.gendocs.list_git_remotes",
        return_value="origin\tgit@github.com:org/repo.git (fetch)\n",
    )

    generate_action_docs(
        input_path=input_path,
        output_path=output_path,
    )

    expected_content = pathlib.Path(
        "tests/gendocs/__fixtures__/EXPECTED.md"
    ).read_text()
    actual_content = output_path.read_text()
    assert expected_content == actual_content
