FROM python:3.12-slim

WORKDIR /srv

# Install dependencies first so this layer stays cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Don't run as root inside the container
RUN useradd --create-home snapchef
USER snapchef

EXPOSE 8000

# Hosting platforms (Render, Railway, ...) tell the app which port to use via $PORT
ENV PORT=8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'"]
