FROM python:3-alpine

# Set the environment variables (and build arguments)
ENV SERVICE_NAME="tlapbot"
ENV FLASK_APP="tlapbot"
ARG UID=911
ARG GID=911

# Run updates and install bash
RUN apk update
RUN apk add bash

# Add a new user named $SERVICE_NAME
RUN addgroup -g ${GID} ${SERVICE_NAME} \
    && adduser -h /app -s /bin/false -D -G ${SERVICE_NAME} -u ${UID} ${SERVICE_NAME}

# Setup the working directory
RUN mkdir /app/instance
RUN chown -R tlapbot. /app/instance
WORKDIR /app

# Copy our project to the correct location
COPY setup.py startup.sh ./
COPY tlapbot ./tlapbot

# Run the production python setup commands
RUN pip install -e .
RUN pip install gunicorn

# Lock down the container settings
USER $SERVICE_NAME
EXPOSE 8000

ENTRYPOINT "/app/startup.sh"
