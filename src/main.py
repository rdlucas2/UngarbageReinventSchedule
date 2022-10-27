import json
import os
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from os.path import exists

token = os.environ.get("TOKEN")

api = FastAPI(title="api")


def load_events(refresh: bool = False):
    results = []

    if refresh or not exists('./static/events.json'):
        url = "https://api.us-east-1.prod.events.aws.a2z.com/attendee/graphql"
        next_token = None
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
    else:
        f = open("./static/events.json")
        results = json.load(f)
        f.close()
    return results


def load_resources(refresh: bool = False):
    resources = []
    if refresh or not exists('./static/resources.json'):
        events = load_events(refresh)
        for e in events:
            if e["venue"] and e["room"]:
                room_name = f"{e['venue']['name']} {e['room']['name']}"
                tmp = "-".join(resources)
                if tmp.find(room_name) == -1:
                    resources.append(room_name)
        resources_file = open("./static/resources.json", "w")
        resources_file.write(json.dumps(resources))
        resources_file.close()
    else:
        f = open("./static/resources.json")
        resources = json.load(f)
        f.close()
    return resources


@api.get("/events")
def read_events(refresh: bool = False):
    events = load_events(refresh)
    print(len(events))
    return {"count": len(events), "data": events}


@api.get("/events/reservable")
def read_reservable(refresh: bool = False):
    events = load_events(refresh)
    result = [e for e in events if e["action"] == "RESERVABLE"]
    print(len(result))
    return {"count": len(result), "data": result}


@api.get("/events/reserved")
def read_reserved(refresh: bool = False):
    events = load_events(refresh)
    result = [e for e in events if e["myReservationStatus"] == "RESERVED"]
    print(len(result))
    return {"count": len(result), "data": result}


@api.get("/events/favorites")
def read_favorites(refresh: bool = False):
    events = load_events(refresh)
    result = [e for e in events if e["isFavoritedByMe"] == True]
    print(len(result))
    return {"count": len(result), "data": result}


@api.get("/resources")
def read_resources(refresh: bool = False):
    return load_resources(refresh)


app = FastAPI(title="site")
app.mount("/api", api)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
