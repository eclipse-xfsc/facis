#-- Base Stage --
FROM debian:stable-slim AS base

ARG DOCKER_USER=default_user

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    gnupg  \
    golang && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r "${DOCKER_USER}" && useradd -r -g "${DOCKER_USER}" "${DOCKER_USER}"


#-- Build Stage --
FROM base AS digital-contracting-service

ARG DOCKER_USER=default_user

RUN mkdir -p /home/${DOCKER_USER}
RUN chmod 0777 /home/${DOCKER_USER}

RUN mkdir -p /app
RUN chown $DOCKER_USER:$DOCKER_USER /app

WORKDIR /app

USER $DOCKER_USER

COPY --chown=$DOCKER_USER:$DOCKER_USER ./ /app/

EXPOSE 8991

CMD ["go",  "run" , "./cmd/dcs"]