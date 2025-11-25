FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://repo.huaweicloud.com/repository/pypi/simple -r requirements.txt

COPY server.py .

CMD ["python3", "server.py"]
