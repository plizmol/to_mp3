FROM jfloff/alpine-python:3.7

RUN apk add curl && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py
RUN echo -e "http://dl-cdn.alpinelinux.org/alpine/edge/community\nhttp://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    apk add  --no-cache ffmpeg && apk upgrade ffmpeg


COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /app
WORKDIR /app

CMD [ "python", "main.py"]