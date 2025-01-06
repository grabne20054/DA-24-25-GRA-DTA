# Use a stable Python version
FROM python:3.10-slim

# Install necessary build tools
RUN apt-get update && apt-get install -y gcc build-essential libssl-dev libffi-dev python3-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the Python path to include the root directory
ENV PYTHONPATH=/src/DataAnalysis

# Copy requirements file
COPY ../requirements.txt /src/DataAnalysis/requirements.txt

# Copy folders to the image
COPY ../descriptive /src/DataAnalysis/descriptive
COPY ../preprocessing /src/DataAnalysis/preprocessing
COPY ../predictive /src/DataAnalysis/predictive
COPY ../predictive/CustomerGrowth /src/DataAnalysis/predictive/CustomerGrowth

# COPY .ENV file
COPY ../.env /src/DataAnalysis/.env

# Install dependencies
RUN pip install -r /src/DataAnalysis/requirements.txt

# Command to run the application
CMD ["python", "/src/DataAnalysis/predictive/CustomerGrowth/CumulativeCustomerGrowthOptimizer.py"]
