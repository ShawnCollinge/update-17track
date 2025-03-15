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
    restart: unless-stopped
networks: {}
```
