FROM alpine:3.10

RUN apk --no-cache add py3-flask py3-psycopg2 py3-gunicorn

RUN addgroup -S snek && adduser -S snek -G snek
WORKDIR /home/snek/app
USER snek
COPY ./api_wsgi.py /home/snek/app/
COPY ./api /home/snek/app/api/

EXPOSE 8123

CMD ["gunicorn", "--worker-tmp-dir", "/tmpfs", "-b", "0.0.0.0:8123", "--workers", "2", "api_wsgi:application"]
