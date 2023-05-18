FROM python:3.10

RUN apt-get update -y && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./ /app/

CMD ["python3", "main.py"]
