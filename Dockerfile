FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps for psycopg
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
    
COPY . .

EXPOSE 8000

#RUN python manage.py collectstatic --noinput

# Run migrations + collectstatic at runtime, then start server
CMD python manage.py makemigrations && \
    python manage.py migrate && \
    gunicorn shop_ai.wsgi:application --bind 0.0.0.0:8000
