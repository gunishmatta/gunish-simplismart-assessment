FROM python:3.9-slim

WORKDIR /app

# Install dependencies and system libraries required for psycopg2-binary
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cp .env.template .env

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
