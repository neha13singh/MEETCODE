# 1. Use an official Python runtime as a parent image
# python:3.11-slim represents a lightweight version of Python 3.11
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Set environment variable to ensure python output is sent straight to terminal (e.g. logs)
ENV PYTHONUNBUFFERED=1

# 4. Install system dependencies required for building Python packages (like gcc) and PostgreSQL client
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file into the container
COPY requirements.txt .

# 6. Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of the application code into the container
COPY . .

# 8. Run the application using uvicorn server
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
