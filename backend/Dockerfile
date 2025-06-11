FROM python:3.12-slim

WORKDIR /fastapi

COPY ./requirements.txt /fastapi/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fastapi/requirements.txt

COPY ./src /fastapi/src

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]