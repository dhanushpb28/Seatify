#!/bin/sh
nginx -g "daemon off;" &
gunicorn Seatify.wsgi:application --bind 0.0.0.0:8000 --workers 3
wait -n
