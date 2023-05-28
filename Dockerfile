FROM registry.access.redhat.com/ubi9/python-311@sha256:004ed4c277683ca3b1ea883b006617a9cc731a164ae2996c11d60b009697ee46

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

USER root
RUN dnf -y install httpd

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Default env vars
ENV PORT 5000

# Install production dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install -r ./requirements.txt
USER nobody

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
