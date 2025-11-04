FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY app.py /app/
COPY seed_db.py /app/
COPY templates /app/templates

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3"]
