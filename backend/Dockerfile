# FROM tiangolo/uvicorn-gunicorn:python3.11-slim
FROM python:3.11-slim

WORKDIR /backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir   

COPY ./backend/ /backend

CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80"]