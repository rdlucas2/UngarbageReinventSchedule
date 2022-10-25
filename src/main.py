import json
import os
import requests
import pytz
from datetime import datetime, timedelta, timezone
from typing import Union
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

token = os.environ.get("TOKEN")

api = FastAPI(title="api")


def load_events():
    f = open("./static/events.json")
    events = json.load(f)
    f.close()
    return events


@api.get("/events")
def read_events():
    events = load_events()
    return {"count": len(events), "data": events}


@api.get("/events/reservable")
def read_reservable():
    events = load_events()
    result = [e for e in events if e["action"] == "RESERVABLE"]
    return {"count": len(result), "data": result}


@api.get("/events/reserved")
def read_reserved():
    events = load_events()
    result = [e for e in events if e["myReservationStatus"] == "RESERVED"]
    return {"count": len(result), "data": result}


@api.get("/events/favorites")
def read_favorites():
    events = load_events()
    result = [e for e in events if e["isFavoritedByMe"] == True]
    return {"count": len(result), "data": result}


@api.get("/seed-resources")
def read_seed_resources():
    events = load_events()
    resources = []
    for e in events:
        if e["venue"] and e["room"]:
            room_name = f"{e['venue']['name']} {e['room']['name']}"
            tmp = "-".join(resources)
            if tmp.find(room_name) == -1:
                resources.append(room_name)
    resources_file = open("./static/resources.json", "w")
    resources_file.write(json.dumps(resources))
    resources_file.close()
    return resources


@api.get("/seed-events")
def read_seed_events():
    url = "https://api.us-east-1.prod.events.aws.a2z.com/attendee/graphql"
    next_token = None
    results = []
    while True:
        payload = json.dumps(
            {
                "operationName": "listAttendeeSessions",
                "variables": {
                    "input": {
                        "eventId": "53b5de8d-7b9d-4fcc-a178-6433641075fe",
                        "maxResults": 97,  # 97 goes into 1746 18 times evenly... the api doesn't return a null nextToken like it's supposed to
                        "nextToken": next_token,
                    }
                },
                "query": "query listAttendeeSessions($input: ListAttendeeSessionsInput!) {\n  listAttendeeSessions(input: $input) {\n    results {\n      ...SessionFragment\n      __typename\n    }\n    totalCount\n    nextToken\n    __typename\n  }\n}\n\nfragment SessionFragment on Session {\n  ...SessionFieldFragment\n  isConflicting {\n    reserved {\n      eventId\n      sessionId\n      isPaidSession\n      __typename\n    }\n    waitlisted {\n      eventId\n      sessionId\n      isPaidSession\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SessionFieldFragment on Session {\n  action\n  alias\n  createdAt\n  description\n  duration\n  endTime\n  eventId\n  isConflicting {\n    reserved {\n      alias\n      createdAt\n      eventId\n      name\n      sessionId\n      type\n      __typename\n    }\n    waitlisted {\n      alias\n      createdAt\n      eventId\n      name\n      sessionId\n      type\n      __typename\n    }\n    __typename\n  }\n  isEmbargoed\n  isFavoritedByMe\n  isPaidSession\n  level\n  location\n  myReservationStatus\n  name\n  sessionId\n  startTime\n  status\n  type\n  capacities {\n    reservableRemaining\n    waitlistRemaining\n    __typename\n  }\n  customFieldDetails {\n    name\n    type\n    visibility\n    fieldId\n    ... on CustomFieldValueFlag {\n      enabled\n      __typename\n    }\n    ... on CustomFieldValueSingleSelect {\n      value {\n        fieldOptionId\n        name\n        __typename\n      }\n      __typename\n    }\n    ... on CustomFieldValueMultiSelect {\n      values {\n        fieldOptionId\n        name\n        __typename\n      }\n      __typename\n    }\n    ... on CustomFieldValueHyperlink {\n      text\n      url\n      __typename\n    }\n    __typename\n  }\n  package {\n    itemId\n    __typename\n  }\n  price {\n    currency\n    value\n    __typename\n  }\n  venue {\n    name\n    __typename\n  }\n  room {\n    name\n    __typename\n  }\n  sessionType {\n    name\n    __typename\n  }\n  speakers {\n    speakerId\n    jobTitle\n    companyName\n    user {\n      firstName\n      lastName\n      __typename\n    }\n    __typename\n  }\n  tracks {\n    name\n    __typename\n  }\n  __typename\n}\n",
            }
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)
        if "errors" in response_dict:
            break
        events = response_dict["data"]["listAttendeeSessions"]["results"]
        results = results + events
        next_token = response_dict["data"]["listAttendeeSessions"]["nextToken"]
        if next_token == None:
            break
    events_file = open("./static/events.json", "w")
    events_file.write(json.dumps(results))
    events_file.close()
    return results


app = FastAPI(title="site")
app.mount("/api", api)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
