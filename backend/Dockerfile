FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000
# Shell form so $PORT expands at runtime — Render/Railway/Heroku inject their
# own PORT and the container must bind to it, not a hardcoded 8000.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
