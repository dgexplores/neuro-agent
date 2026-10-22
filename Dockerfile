FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements-lambda.txt ./
RUN pip install --no-cache-dir --only-binary=:all: -r requirements-lambda.txt
COPY backend/ ./backend/
COPY data/ ./data/
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
