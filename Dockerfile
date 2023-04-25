FROM python:3.11.3-bullseye

ENV PYTHONDONTWRITEBYTECODE 1

COPY . app/
WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

CMD [ "gunicorn", "app:app", "--bind", "0.0.0.0:8080" ]
