# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /usr/src/API

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements file
COPY ./API/requirements.txt /usr/src/API/requirements.txt

# install dependencies
RUN set -eux \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cmake \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/API/requirements.txt \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip

EXPOSE 8000

# copy project
COPY DataAnalysis /usr/src/DataAnalysis
COPY API /usr/src/DataAnalysis

# set PYTHONPATH
ENV PYTHONPATH=/usr/src

CMD ["uvicorn", "API.api.main:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
