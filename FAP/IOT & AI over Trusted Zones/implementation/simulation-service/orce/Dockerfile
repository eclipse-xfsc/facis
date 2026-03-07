FROM ecofacis/xfsc-orce:2.0.3

USER root

# Install pre-built librdkafka and build tools from Alpine repos.
RUN apk add --no-cache librdkafka-dev python3 make g++

# Install node-red-contrib-rdkafka into a staging directory.
# We cannot install directly into /data (Docker volume mounted at runtime)
# or /opt/maestro (managed by ORCE). A staging dir lets us copy at startup.
RUN mkdir -p /opt/rdkafka-staging && \
    cd /opt/rdkafka-staging && \
    npm init -y && \
    npm install node-red-contrib-rdkafka

# Patched rdkafka.js with SSL/mTLS support for cluster Kafka connections.
COPY rdkafka-patch.js /opt/rdkafka-staging/rdkafka-patch.js

# Custom entrypoint: copies rdkafka into /data/node_modules at startup,
# applies SSL patch, then delegates to the original ORCE entrypoint.
COPY entrypoint.sh /usr/local/bin/entrypoint-rdkafka.sh
RUN chmod +x /usr/local/bin/entrypoint-rdkafka.sh

ENTRYPOINT ["/usr/local/bin/entrypoint-rdkafka.sh"]

# Do NOT switch to node-red here — the original ORCE entrypoint runs as root
# and handles the user switch internally (run_as_node_red / su-exec).
