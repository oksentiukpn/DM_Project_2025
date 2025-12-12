FROM python:3.13-slim

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY . /app

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
