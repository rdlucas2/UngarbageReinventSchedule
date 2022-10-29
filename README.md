# UngarbageReinventSchedule
The reinvent scheduler/calendar is garbage.

#### Loading events:
On initial visit, you must provide your jwt auth bearer token (use your browser dev tools to find it on the re:invent site) - then hit the load button. Events are stored in IndexDB in your local browser. Use the checkbox and change the filter to force a refresh of events (bearer token must be provided when doing this as well).

### Develop locally with docker:
```
docker build -t ungarbage-dev --target development .
docker run --rm -it -v "$(pwd)\src:/usr/src/app" --env-file local.env -p 8000:8000 --name=ungarbage-dev ungarbage-dev
```

### Build artifact with docker:
```
docker build -t ungarbage --target artifact .
docker run --rm -it -v "$(pwd)\src:/usr/src/app" --env-file local.env -p 8000:8000 --name=ungarbage ungarbage
```

### Debug inside container:
```
docker run --rm -it -v "$(pwd)\src:/usr/src/app" --env-file local.env -p 8000:8000 --name=ungarbage --entrypoint /bin/bash ungarbage
```


### TODO:
- make events exportable to outlook and/or google calendar (ics format?)
- hover/click actions to display details of event
