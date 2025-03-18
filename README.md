# Parses email and updates 17track.net tracking


Can be used with docker compose:

```
version: "3.9"
services:
  sync-17track:
    image: scollinge/sync-17track:latest
    environment:
      - SEVENTEEN_EMAIL= 
      - SEVENTEEN_PASSWORD= 
      - TRACKING_EMAIL= 
      - TRACKING_PASSWORD= 
```

## Environment Variables

| Variable Name        | Description                                             | Default Value |
|----------------------|---------------------------------------------------------|--------------|
| `IMAP_SERVER`       | IMAP server address for email retrieval                 | `imap.gmail.com` | 
| `IMAP_PORT`         | IMAP server port (usually `993` for SSL)                | `993`        | 
| `USE_SSL`           | Whether to use SSL for IMAP connection (`true`/`false`) | `true`       |
| `TRACKING_EMAIL`    | Email address used for tracking orders                  | ❌ None      |
| `TRACKING_PASSWORD` | Password for the tracking email account                 | ❌ None      |
| `TRACKING_FOLDER`   | Email folder where tracking emails are stored            | `INBOX`      | 
| `DAYS_OLD`          | Number of days back to search for emails                | `30`         |
| `SEVENTEEN_EMAIL`   | Email for 17Track login                                 | ❌ None      |
| `SEVENTEEN_PASSWORD`| Password for 17Track login                              | ❌ None      | 
| `ARCHIVE_DELIVERED`  | Whether to archive delivered packages (`True`/`False`)   | `True`       |

---




## Automate every 12h with ofelia

```
version: "2"
services:
  scheduler:
    image: mcuadros/ofelia:latest
    container_name: scheduler
    command: daemon --docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      ofelia.job-run.sync-17track.schedule: "@every 12h"
      ofelia.job-run.sync-17track.container: sync-17track
    restart: unless-stopped
  sync-17track:
    container_name: sync-17track
    image: scollinge/sync-17track:latest
    environment:
      - SEVENTEEN_EMAIL=
      - SEVENTEEN_PASSWORD=
      - TRACKING_EMAIL=
      - TRACKING_PASSWORD=
    restart: no
```