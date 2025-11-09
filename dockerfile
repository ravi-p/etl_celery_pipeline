# Dockerfile
FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the entire app directory
COPY app/ app/
# Ensure the data directory exists for SQLite
RUN mkdir -p data
CMD ["tail", "-f", "/dev/null"] # Keep container running