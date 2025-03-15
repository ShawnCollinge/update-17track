#!/bin/sh

exec python3 /app/main.py

cron &

exec tail -f /var/log/cron.log