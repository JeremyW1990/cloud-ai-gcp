FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Make sure the script is executable
RUN chmod +x main.py

# Use environment variables to pass the port
ENV PORT=8080

CMD ["python", "main.py"]