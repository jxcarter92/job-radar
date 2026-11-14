FROM python:3.13-slim
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN pip uninstall -y pip

COPY fetch.py ./

RUN useradd -u 10001 app
USER app

CMD ["python", "fetch.py"]