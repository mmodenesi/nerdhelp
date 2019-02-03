FROM python:2.7.15-jessie

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./manage.py /app/manage.py
COPY ./definitions /app/definitions
COPY ./nerdhelp /app/nerdhelp
COPY ./scripts /app/scripts

WORKDIR /app

EXPOSE 80

VOLUME "/app/media"

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
