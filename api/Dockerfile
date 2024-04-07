FROM python:3.12

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY src/ .

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
