FROM python:3.13-slim

WORKDIR /app
# Adding requirements.txt
COPY requirements.txt ./

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . /app

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
