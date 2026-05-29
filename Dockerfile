FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY . .

RUN chmod +x /app/entrypoint.sh

CMD ["sh", "/app/entrypoint.sh"]

HEALTHCHECK CMD curl --fail http://localhost:8000/docs || exit 1