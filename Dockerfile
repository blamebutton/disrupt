FROM python:3

ENV DOCKER_HOST='unix:///var/run/docker.sock'

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENTRYPOINT ["/app/main.py"]