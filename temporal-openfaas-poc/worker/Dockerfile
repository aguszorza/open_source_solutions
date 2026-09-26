FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY activities ./activities
COPY workflows ./workflows
COPY worker.py .


CMD ["python", "worker.py"]