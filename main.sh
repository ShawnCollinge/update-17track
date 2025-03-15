#!/bin/sh

cron &

exec python3 /app/main.py
