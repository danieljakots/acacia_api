FROM alpine:3.9

COPY ./api_wsgi.py /app/
COPY ./api /app/api/
#RUN pip install -r /app/api/requirements.txt

RUN apk --no-cache add py3-flask py3-psycopg2 py3-gunicorn

WORKDIR /app

EXPOSE 8123

CMD ["gunicorn", "-b", "0.0.0.0:8123", "--workers", "2", "api_wsgi:application"]
