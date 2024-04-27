FROM python:3.12-alpine

WORKDIR /opt/functional

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY src/ .

ENTRYPOINT ["pytest", "/opt/functional/tests"]
