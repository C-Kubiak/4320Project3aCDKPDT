# Use an official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]

RUN pip install matplotlib

RUN pip install pandas