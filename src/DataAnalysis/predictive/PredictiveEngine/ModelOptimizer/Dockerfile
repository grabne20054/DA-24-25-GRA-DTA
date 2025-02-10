# Use a stable Python version
FROM python:3.10-slim

# Install necessary build tools
RUN apt-get update && apt-get install -y gcc build-essential libssl-dev libffi-dev python3-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the Python path to include the root directory
ENV PYTHONPATH=/app

WORKDIR /app

COPY DataAnalysis/predictive/requirements.txt predictive/requirements.txt

COPY . .

# Install dependencies
RUN pip install -r DataAnalysis/predictive/requirements.txt

# Command to run the application
CMD ["python", "DataAnalysis/predictive/PredictiveEngine/ModelOptimizer/ModelOptimizer.py"]

