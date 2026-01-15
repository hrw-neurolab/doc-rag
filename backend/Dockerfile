FROM python:3.12-slim

WORKDIR /fastapi

RUN apt-get update && apt-get install -y \
    binutils \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /fastapi/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fastapi/requirements.txt

COPY ./src /fastapi/src

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]