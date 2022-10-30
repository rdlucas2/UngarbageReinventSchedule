# UngarbageReinventSchedule
The reinvent scheduler/calendar is garbage. View the calendar here: [https://rdlucas2.github.io/UngarbageReinventSchedule/](https://rdlucas2.github.io/UngarbageReinventSchedule/)

#### Loading events:
On initial visit, you must provide your jwt auth bearer token (use your browser dev tools to find it on the re:invent site) - then hit the load button (may take a minute or so to load events from aws). Events are stored in IndexedDB in your local browser. Use the checkbox and change the filter to force a refresh of events (bearer token must be provided when doing this as well).

### developing
It's a static html file with a lot of javascript. No fancy build tools needed.

### TODO:
- make events exportable to outlook and/or google calendar (ics format?)
- hover/click actions to display details of event
