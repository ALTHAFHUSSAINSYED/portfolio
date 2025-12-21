FROM python:3.10-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && apt-get remove -y build-essential curl \
    && apt-get autoremove -y \
    && rm -rf /root/.cache/pip

COPY backend /app/backend

COPY start.sh .
RUN chmod +x start.sh

WORKDIR /app

EXPOSE 8000

CMD ["sh", "start.sh"]
