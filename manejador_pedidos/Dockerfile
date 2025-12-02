FROM python:3.10-slim

WORKDIR /app
COPY .. /app

ENV DATABASE_HOST=<DATABASE_HOST>

RUN apt-get update \
    && apt-get install -y gcc libpq-dev python3-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "init.sh"]
