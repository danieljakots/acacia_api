#!/bin/sh
rsync -Parv --delete ./api web0:/home/api/
rsync -Parv --delete ./html/* web0:/var/www/api.chown.me
#ssh abitibi "doas rcctl restart gunicorn_api"
