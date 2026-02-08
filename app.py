from typing import Any
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json

from apify import Client
from gemini import GeminiClient
from session import SessionStore

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

client = Client()
gemini = GeminiClient()
sessions = SessionStore()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


PROMPT = """
Extract the relevant fields from the user messages (if possible) and return a JSON with each field and its value. 
treat the messages as a stack from earliest to latest, and try to extract the most up-to-date information from the messages. if there are conflicting information in the messages, prefer the latest message.

The fields to extract are:
 "job_title": a string representing the job title the user is interested in,
 "location": a string can be a city, area or a state/country representing the location of the job, try to convert it to something specific according to the context.
 "company_names": a list of strings representing the company names the user is interested in, e.g. Google, Facebook, ...
 "experience_level": string between 1-6, i.e. "1", "2", or "3"

* If "company_names" is startups or tech or something vague expand it to actual company names in that location and definition.
* Do not include a missing fields that cannot be extracted in the JSON.
* if you have enough information return the JSON with the extracted fields and a continuation message (add it to the JSON as "message"). 
* Otherwise return a JSON with "continuation" asking the user for the missing information. The continuation message should be a string that can be directly sent to the user.
* no markdown, only return the JSON

Rules for required fields:
- job_title is required, if it's missing return a continuation message asking the user to specify the
- location is required, if it's missing return a continuation message asking the user to specify the location
- company_names preferred, suggest the user adds it to get better results
- experience_level is not required, if it's missing you can assume the user is open to all
 
user messages:
{user_messages}
"""


# 3. Create the POST endpoint
@app.post("/get_jobs")
async def handle_message(data: UserRequest):
    print(f"Received message: {data.message}")

    session = sessions.get_session(data.session_id)
    session.add(data.message)

    prompt = PROMPT.format(user_messages=session.get_messages())
    result = gemini.generate_content(contents=prompt)

    print(result)
    data = json.loads(result)
    if "continuation" in data:
        return {"status": "continuation", "message": data["continuation"]}

    data["jobs_entries"] = 20
    res = client.call(data)
    # with open("output.json", "w") as f:
    #     json.dump(output_res, f, indent=4)

    return {"status": "success", "jobs": res, "message": data.get("message", "")}

with open("index.html", "r") as f:
    HTML = f.read()

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

# # Prepare the Actor input
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
