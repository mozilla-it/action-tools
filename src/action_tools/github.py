import re
from typing import Optional
from urllib.parse import parse_qsl, urlparse

import httpx


class ClientError(Exception):
    def __init__(
        self,
        message: str,
        request: httpx.Request,
        response: httpx.Response,
    ):
        super().__init__(message)
        self.request = request
        self.response = response


MAX_PER_PAGE = 100


class Client:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
    ):
        self.token = token
        self.base_url = base_url

    def _get(self, endpoint: str, params: Optional[dict] = None) -> httpx.Response:
        with httpx.Client() as client:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
            }
            resp = client.get(self.base_url + endpoint, headers=headers, params=params)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise ClientError(
                    str(exc),
                    request=exc.request,
                    response=exc.response,
                ) from exc
        return resp

    def _paginate(
        self, endpoint: str, params: Optional[dict] = None, max_pages: int = 10
    ) -> list:
        items = []
        pages_fetched = 0
        current_endpoint = endpoint
        current_params = params or {}

        while current_endpoint and pages_fetched < max_pages:
            resp = self._get(current_endpoint, params=current_params)

            data = resp.json()
            items.extend(data.get("items", []))
            pages_fetched += 1

            link_header = resp.headers.get("link")
            if not link_header:
                break
            # used to match the `link:` headers as described here
            # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28#using-link-headers
            if match := re.search(r'<(?P<next_url>[^>]+)>;\s*rel="next"', link_header):
                parsed = urlparse(match.group("next_url"))
                current_endpoint = parsed.path
                current_params = dict(parse_qsl(parsed.query))
            else:
                break

        return items

    def get_repo_contents(self, org: str, repo: str, subpath: str = "") -> list:
        endpoint = f"/repos/{org}/{repo}/contents{subpath}"
        return self._get(endpoint).json()

    def search_code(self, query: str, max_pages=10) -> list:
        endpoint = "/search/code"
        params = {"q": query, "per_page": MAX_PER_PAGE}
        results = self._paginate(endpoint, params=params, max_pages=max_pages)
        return results
