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
      - TRACKING_EMAIL_PASSWORD= 
```

## Environment Variables

| Variable Name        | Description                                             | Default Value |
|----------------------|---------------------------------------------------------|--------------|
| `IMAP_SERVER`       | IMAP server address for email retrieval                 | `imap.gmail.com` | 
| `IMAP_PORT`         | IMAP server port (usually `993` for SSL)                | `993`        | 
| `USE_SSL`           | Whether to use SSL for IMAP connection (`true`/`false`) | `true`       |
| `TRACKING_EMAIL`    | Email address used for tracking orders                  | ❌ None      |
| `TRACKING_PASSWORD` | Password for the tracking email account                 | ❌ None      |
| `TRACKING_FOLDER`   | IMAP folder where tracking emails are stored            | `INBOX`      | 
| `DAYS_OLD`          | Number of days back to search for emails                | `30`         |
| `SEVENTEEN_EMAIL`   | Email for 17Track login                                 | ❌ None      |
| `SEVENTEEN_PASSWORD`| Password for 17Track login                              | ❌ None      | 
| `REMOVE_DELIVERED`  | Whether to remove delivered packages (`True`/`False`)   | `True`       |

---