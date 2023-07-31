# FROM tiangolo/uvicorn-gunicorn:python3.8
FROM python:3.9

LABEL maintainer="Paulo Mota <phmota@outlook.com.br>"

RUN pip install fastapi uvicorn gunicorn

COPY . .

RUN  pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn"  , "main:app", "--host", "0.0.0.0", "--port", "80"]