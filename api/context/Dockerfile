# Use a base image that supports Python
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files and folders
COPY api/context /app/api/context
COPY api/vendor/vendor_strategy.py /app/api/vendor/vendor_strategy.py
COPY api/vendor/base_strategy.py /app/api/vendor/base_strategy.py   
COPY api/vendor/openai/main.py /app/api/vendor/openai/main.py
COPY api/vendor/claude/main.py /app/api/vendor/claude/main.py
COPY api/utils/ /app/api/utils/


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r api/context/requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Set the default command to run the Python file
CMD ["python", "api/context/main.py"]
