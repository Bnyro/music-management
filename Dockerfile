# set base image (host OS)
FROM python:3.11

# set the working directory in the container
WORKDIR /app

# update the system
RUN apt-get update

# install ffmpeg for downloading music
RUN apt-get install -y ffmpeg

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./ .

# command to run on container start
CMD [ "gunicorn", "main:app", "-b", "0.0.0.0:8000" ] 

EXPOSE 8000
