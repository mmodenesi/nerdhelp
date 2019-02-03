FROM python:2.7.15-jessie

WORKDIR /app

RUN apt-get update && \
    apt-get install texlive-full -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

VOLUME "/app/media"

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
