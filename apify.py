from typing import Any, AsyncGenerator
from apify_client import ApifyClientAsync


# Actor input fields
# run_input = {
#     "job_title": "Software Engineer",
#     "location": "United States",
#     "jobs_entries": 100,
#     "company_names": ["Google", "Microsoft", "Amazon", "Facebook", "Apple"],
#     # "experience_level": None,
#     # "job_type": None,
#     # "work_schedule": None,
#     # "job_post_time": None,
#     # "start_jobs": 0,
# }


class Client:
    RUN_ID = "JkfTWxtpgfvcRQn3p"

    def __init__(self, token: str):
        self._client = ApifyClientAsync(token)

    async def call(self, input: dict) -> AsyncGenerator[dict[str, Any], dict]:
        run = await self._client.actor(self.RUN_ID).call(run_input=input)
        async for item in self._client.dataset(run["defaultDatasetId"]).iterate_items(limit=10):
            yield item
