FROM python:3.12

RUN apt-get update && apt-get install -y \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 7776

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7776", "--reload"]