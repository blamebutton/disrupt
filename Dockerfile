FROM python:3.8-alpine

ENV DOCKER_HOST='unix:///var/run/docker.sock'

WORKDIR /app
COPY main.py requirements.txt /app/
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
