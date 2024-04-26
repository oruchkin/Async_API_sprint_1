FROM python:3.12-alpine

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY src/ .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "main:app", "--log-level=debug", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
