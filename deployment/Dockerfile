FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY backend/ ./backend/

EXPOSE 5000

ENV FLASK_APP=backend/app.py

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]
