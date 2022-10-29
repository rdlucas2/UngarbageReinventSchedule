import json
import requests
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

api = FastAPI(title="api")


def load_events(token: str):
    results = []
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
    return results


@api.get("/events")
def read_events(request: Request):
    events = load_events(request.headers.get("aws-bearer-token"))
    return {"count": len(events), "data": events}
    # hack = """
    # [{
    #     "action": "NO_SEATING",
    #     "alias": "ACT017",
    #     "createdAt": 1665264869296,
    #     "description": "Make your voice heard here! Visit our sticker wall for fun questions. ",
    #     "duration": 480,
    #     "endTime": 1669597200000,
    #     "eventId": "53b5de8d-7b9d-4fcc-a178-6433641075fe",
    #     "isConflicting": {
    #         "reserved": [],
    #         "waitlisted": [],
    #         "__typename": "SessionConflicts"
    #     },
    #     "isEmbargoed": false,
    #     "isFavoritedByMe": false,
    #     "isPaidSession": false,
    #     "level": null,
    #     "location": null,
    #     "myReservationStatus": "NONE",
    #     "name": "AWS community stickers ",
    #     "sessionId": "1d3b3a6d-fc3e-4db0-928a-18eadb5adade",
    #     "startTime": 1669568400000,
    #     "status": "published",
    #     "type": "breakout",
    #     "capacities": {
    #         "reservableRemaining": 0,
    #         "waitlistRemaining": -1,
    #         "__typename": "SessionCapacity"
    #     },
    #     "customFieldDetails": [
    #         {
    #             "name": "Additional Activities",
    #             "type": "MULTI_SELECT",
    #             "visibility": "PUBLIC",
    #             "fieldId": "26f6ecd0-fdf4-49c6-bfbf-df6aa36a7ccb",
    #             "values": [
    #                 {
    #                     "fieldOptionId": "fd333a9b-e3e5-4c87-9a49-a38f1eee7c8d",
    #                     "name": "Community",
    #                     "__typename": "CustomFieldOptionValue"
    #                 }
    #             ],
    #             "__typename": "CustomFieldValueMultiSelect"
    #         }
    #     ],
    #     "package": null,
    #     "price": null,
    #     "venue": {
    #         "name": "Venetian",
    #         "__typename": "Venue"
    #     },
    #     "room": {
    #         "name": "Level 2, Hall B Foyer, Sticker Activation",
    #         "__typename": "Room"
    #     },
    #     "sessionType": {
    #         "name": "Community Activities",
    #         "__typename": "SessionType"
    #     },
    #     "speakers": [],
    #     "tracks": [],
    #     "__typename": "Session",
    #     "id": 0
    # },
    # {
    #     "action": "NO_SEATING",
    #     "alias": "ACT018",
    #     "createdAt": 1665264871190,
    #     "description": "Lounge, relax, and connect in our FUNctional Lounge. Powered tables and seating are available so you can work and recharge.",
    #     "duration": 480,
    #     "endTime": 1669597200000,
    #     "eventId": "53b5de8d-7b9d-4fcc-a178-6433641075fe",
    #     "isConflicting": {
    #         "reserved": [],
    #         "waitlisted": [],
    #         "__typename": "SessionConflicts"
    #     },
    #     "isEmbargoed": false,
    #     "isFavoritedByMe": false,
    #     "isPaidSession": false,
    #     "level": null,
    #     "location": null,
    #     "myReservationStatus": "NONE",
    #     "name": "FUNctional Lounge",
    #     "sessionId": "baf429b9-3c7b-457a-b8bc-3707d08e8d5b",
    #     "startTime": 1669568400000,
    #     "status": "published",
    #     "type": "breakout",
    #     "capacities": {
    #         "reservableRemaining": 0,
    #         "waitlistRemaining": -1,
    #         "__typename": "SessionCapacity"
    #     },
    #     "customFieldDetails": [],
    #     "package": null,
    #     "price": null,
    #     "venue": {
    #         "name": "Venetian",
    #         "__typename": "Venue"
    #     },
    #     "room": {
    #         "name": "Level 2, Artist Lounge",
    #         "__typename": "Room"
    #     },
    #     "sessionType": {
    #         "name": "Community Activities",
    #         "__typename": "SessionType"
    #     },
    #     "speakers": [],
    #     "tracks": [],
    #     "__typename": "Session",
    #     "id": 1
    # }]
    # """
    # print(hack)
    # events = json.loads(hack)
    # print(events)
    # return {"count": len(events), "data": events}


app = FastAPI(title="site")
app.mount("/api", api)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
