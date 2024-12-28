# Base image
FROM python:3.9-slim

# Install MLflow and other dependencies
RUN pip install --no-cache-dir mlflow boto3 psycopg2-binary

# Expose the default MLflow port
EXPOSE 5000

# Set the working directory
WORKDIR /mlflow

# Command to run the MLflow server
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
