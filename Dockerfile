FROM registry.access.redhat.com/ubi9/python-39@sha256:40a58935b9c22664927b22bf256f53a3d744ddb7316f3af18061099e199526ee

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

USER root
RUN dnf -y install httpd

# Copy only requirements.txt
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt ./

# Install production dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install -r ./requirements.txt
USER nobody

# Copy code and set env var
COPY searcher ./searcher
COPY .chroma ./.chroma
ENV PORT 5000

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 'searcher:create_app()'
