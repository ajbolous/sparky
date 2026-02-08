from typing import Any, Iterator
from apify_client import ApifyClient


class Client:
    RUN_ID = "JkfTWxtpgfvcRQn3p"

    def __init__(self, token: str):
        self._client = ApifyClient(token)

    def call(self, input: dict) -> Iterator[dict[str, Any]]:
        run = self._client.actor(self.RUN_ID).call(run_input=input)
        for item in self._client.dataset(run["defaultDatasetId"]).iterate_items():
            yield item
