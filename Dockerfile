FROM python:3.12-alpine3.18

RUN addgroup --gid 8042 -S snek && adduser --uid 8042 -S snek -G snek
WORKDIR /home/snek/app
COPY ./requirements.txt /home/snek/requirements.txt

RUN  \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 pip install --no-cache-dir -r /home/snek/requirements.txt && \
 apk --purge del .build-deps

USER snek
COPY ./wsgi.py /home/snek/app/
COPY ./api /home/snek/app/api/

EXPOSE 8123

CMD ["gunicorn", "--log-file=-", "--access-logfile=-", "--worker-tmp-dir", \
     "/tmpfs", "-b", "0.0.0.0:8123", "--workers", "8", "wsgi:application"]
