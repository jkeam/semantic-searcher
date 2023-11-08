FROM registry.access.redhat.com/ubi9/python-39@sha256:c7a34a3cb7833ca587c841f7c1716f0d9964ab6af76b69cf2831c90faf7697f1

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

USER root
RUN dnf -y install httpd

# Upgrade sqlite3
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3410200.tar.gz && \
    tar xvfz sqlite-autoconf-*.tar.gz && \
    cd sqlite-autoconf-3410200 && \
    ./configure --prefix=/usr && \
    make -j 1 && \
    make install

# Copy only requirements.txt
ENV APP_HOME /opt/app-root/src
WORKDIR $APP_HOME
COPY requirements.txt ./

# Install production dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install -r ./requirements.txt
USER nobody

# Copy code and set env var
COPY searcher ./searcher
ENV PORT 5000

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 'searcher:create_app()'
