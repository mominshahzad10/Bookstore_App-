FROM python:3.9-slim

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy your application code
COPY . .

# Specify the command to run your Flask app
CMD ["python", "./app.py"]
