# UngarbageReinventSchedule
The reinvent scheduler/calendar is garbage.

#### Loading events:
On initial visit, you must provide your jwt auth bearer token (use your browser dev tools to find it on the re:invent site) - then hit the load button. Events are stored in IndexDB in your local browser. Use the checkbox and change the filter to force a refresh of events (bearer token must be provided when doing this as well).

### developing
It's a static html file with a lot of javascript. No fancy build tools needed.

### TODO:
- make events exportable to outlook and/or google calendar (ics format?)
- hover/click actions to display details of event
