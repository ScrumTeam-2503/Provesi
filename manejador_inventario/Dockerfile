FROM python:3.8.10-alpine3.13

WORKDIR /app

COPY . /app

ENV DATABASE_HOST <DATABASE_HOST>

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "init.sh"]
