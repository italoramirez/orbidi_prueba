FROM python:3.9

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN python3 -m pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]

