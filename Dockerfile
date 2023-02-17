FROM python:3.10.4-alpine3.15


ENV PYTHONUNBUFFERED=1


RUN apk update
WORKDIR /app
COPY /src/requirements.txt ./
RUN pip install -r requirements.txt

COPY ./ ./

EXPOSE 8000

CMD ["python3","./src/app.py"]