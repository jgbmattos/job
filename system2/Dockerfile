FROM ubuntu:latest
MAINTAINER João Mattos "jgbmattos@gmail.com"
RUN apt-get update && apt-get install -y python-pip
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]