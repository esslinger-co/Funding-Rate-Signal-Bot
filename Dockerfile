FROM python:3.12-slim

WORKDIR /app

# Installiere Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Bot
COPY bot.py .

# Setze Environment
ENV PYTHONUNBUFFERED=1

# Run Bot
CMD ["python", "bot.py"]
