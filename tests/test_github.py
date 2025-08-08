import pytest

from action_tools.github import Client, ClientStatusError


@pytest.fixture
def github_client():
    return Client(base_url="https://www.example.com", token="fake-token")


def test_get_repo_contents_success(github_client, respx_mock):
    mock_url = f"{github_client.base_url}/repos/testorg/testrepo/contents"
    respx_mock.get(mock_url).respond(200, json=[{"name": "README.md"}])

    result = github_client.get_repo_contents("testorg", "testrepo")
    assert isinstance(result, list)
    assert result[0]["name"] == "README.md"


def test_get_repo_contents_not_found(github_client, respx_mock):
    mock_url = f"{github_client.base_url}/repos/testorg/testrepo/contents"
    respx_mock.get(mock_url).respond(404, json={"message": "Not Found"})

    with pytest.raises(ClientStatusError) as exc_info:
        github_client.get_repo_contents("testorg", "testrepo")
    assert "404" in str(exc_info.value)
    assert exc_info.value.status_code == 404


def test_search_code_success(github_client, respx_mock):
    query = "test in:file repo:testorg/testrepo"
    mock_url = f"{github_client.base_url}/search/code"
    respx_mock.get(mock_url, params={"q": query}).respond(
        200, json={"items": [{"name": "file1.py"}]}
    )

    results = github_client.search_code(query)
    assert isinstance(results, list)
    assert results[0]["name"] == "file1.py"


def test_search_code_pagination(github_client, respx_mock):
    query = "test in:file repo:testorg/testrepo"
    url = f"{github_client.base_url}/search/code"

    link_header = '<https://www.example.com/search/code?q=test+in%3Afile+repo%3Atestorg%2Ftestrepo&per_page=100&page=2>; rel="next"'
    # order matters with these mocks -- need the 2nd page's mock first since both `GETs` will match the first page's url + query params
    respx_mock.get(url, params={"q": query, "per_page": "100", "page": "2"}).respond(
        200,
        json={"items": list({"name": f"file{n}.py"} for n in range(101, 201))},
    )
    respx_mock.get(url, params={"q": query, "per_page": "100"}).respond(
        200,
        json={"items": list({"name": f"file{n}.py"} for n in range(1, 101))},
        headers={"link": link_header},
    )

    results = github_client.search_code(query, max_pages=2)
    assert isinstance(results, list)
    assert len(results) == 200
    assert results[0]["name"] == "file1.py"
    assert results[-1]["name"] == "file200.py"


def test_search_code_empty_results(github_client, respx_mock):
    query = "nonexistent"
    mock_url = f"{github_client.base_url}/search/code"
    respx_mock.get(mock_url, params={"q": query}).respond(200, json={"items": []})

    results = github_client.search_code(query)
    assert results == []
