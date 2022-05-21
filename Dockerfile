FROM python:3.9.6

WORKDIR /code

COPY requirements.txt requirements-dev.txt /code/

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt -r /code/requirements-dev.txt

COPY ./comment /code/comment

CMD ["uvicorn", "comment.main:app", "--host", "0.0.0.0", "--loop", "uvloop", "--log-config", "comment/logging.json"]
