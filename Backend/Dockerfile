FROM python:3.13.7-alpine3.21

WORKDIR /usr/app/backend

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

