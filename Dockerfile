FROM python:3.10-buster

RUN apt update
RUN apt install build-essential
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./.env eform/.env
RUN python manage.py makemigrations
RUN python manage.py migrate
EXPOSE 8082
CMD ["gunicorn", "-b", "0.0.0.0:8082", "eform.wsgi:application"]
