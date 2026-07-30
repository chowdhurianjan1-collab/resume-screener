FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

COPY . .

EXPOSE 8000
# Shell form so $PORT expands at runtime — Render/Railway/Heroku inject their
# own PORT and the container must bind to it, not a hardcoded 8000.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
