from typing import Any
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from google.genai import types

from apify import Client
from gemini import GeminiChatSessions

GEMINI_KEY = os.environ.get("GEMINI_KEY", None)
APIFY_KEY = os.environ.get("APIFY_KEY", None)

class UserRequest(BaseModel):
    session_id: str
    message: str


class JobResponse(BaseModel):
    title: str
    company: str
    location: str
    description: str
    link: str

    metadata: dict[str, Any]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Client(APIFY_KEY)

SYSTEM_PROMPT = """
Act as a job search assistant called Sparky. Your task is to extract relevant information from the user's messages and prepare a structured JSON that can be used to perform a job search query.

Tools available:
1) job_search: Retrieves a list of relevant jobs for the given query context and user preferences. The input to this tool should be the following fields(args):
- job_title: a string representing the job title the user is interested in
- location: a string can be a city, area or a state/country representing the location of the job, try to convert it to something specific according to the context.
- company_names: a list of strings representing the company names the user is interested in, e

* If "company_names" is startups or tech or something vague expand it to actual company names in that location and definition.
* Do not include a missing fields that cannot be extracted in the JSON.
* if you have enough information call the tool and return a continuation message (add it to the JSON as "message"). Otherwise guide the user to give you the missing information.

Rules for required fields:
- job_title is required, if it's missing return a continuation message asking the user to specify the
- location is required, if it's missing return a continuation message asking the user to specify the location
- company_names preferred, suggest the user adds it to get better results
- experience_level is not required, if it's missing you can assume the user is open to all
"""

tools_declarations = [
    {
        "name": "job_search",
        "description": (
            "Calls the job search API and return a list of relevant jobs for the given query context and user preferences."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "description": "The job title to search for, e.g. Software Engineer, Data Scientist, ...",
                },
                "location": {
                    "type": "string",
                    "description": "The location to search for jobs in, e.g. United States, California, San Francisco, ...",
                },
                "company_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "User query text",
                },
            },
            "required": ["job_title", "location"],
        },
    },
]

tools = [types.Tool(function_declarations=tools_declarations)]
config = types.GenerateContentConfig(
    tools=tools, max_output_tokens=5000, system_instruction=SYSTEM_PROMPT
)
sessions = GeminiChatSessions(config=config, api_key=GEMINI_KEY)


async def _handle_function_calls(
    function_calls: list[types.FunctionCall],
) -> tuple[dict[str, Any], str]:
    if not function_calls:
        return None, "CONVERSE"

    for fcall in function_calls:
        args = fcall.args or {}
        if fcall.name == "job_search":
            data = {
                "job_title": args.get("job_title"),
                "location": args.get("location"),
                "company_names": args.get("company_names", []),
                "job_entries": "10",
            }
            print("Calling apify with data:", data)
            res = [obj async for obj in client.call(data)]
            return res, "SEARCH"

    return None, "CONVERSE"


# 3. Create the POST endpoint
@app.post("/get_jobs")
async def handle_message(data: UserRequest):

    session = sessions.get_session(data.session_id)
    result = session.send_message(data.message)
    print(result)
    search_result, intent = await _handle_function_calls(result.function_calls)
    if intent == "CONVERSE":
        return {"status": "continuation", "message": result.text}

    continuation_message = sessions.generate_content(
        f"""Create a very short summary of the following results and reason their relevance for the query
            Query: {data.message}
            Results: {[o['job_title'] for o in search_result]}
            """
    )
    return {"status": "success", "jobs": search_result, "message": continuation_message}


with open("index.html", "r") as f:
    HTML = f.read()


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


@app.get("/health")
def health_check():
    return {"status": "healthy"}

