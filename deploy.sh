#!/bin/sh
rsync -Parv --delete ./api abitibi:/home/api/
rsync -Parv --delete ./html/* abitibi:/var/www/api.chown.me
#ssh abitibi "doas rcctl restart gunicorn_api"
