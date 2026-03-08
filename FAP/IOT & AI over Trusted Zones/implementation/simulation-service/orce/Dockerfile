FROM ecofacis/xfsc-orce:2.0.3

USER root

# ── System dependencies ──────────────────────────────────────────────
# librdkafka-dev: native Kafka client for node-red-contrib-rdkafka
# python3, make, g++: required for native npm module compilation
RUN apk add --no-cache librdkafka-dev python3 make g++

# Fix node-gyp compatibility with Node 20.19.
# The ORCE base image ships npm 11.6.0 whose bundled node-gyp has a broken
# logger (TypeError: Cannot read properties of undefined 'pause').
# Updating npm brings a fixed node-gyp.
RUN npm install -g npm@latest

# ── Kafka plugin (rdkafka) ───────────────────────────────────────────
# Install node-red-contrib-rdkafka into a staging directory.
# We cannot install directly into /data (Docker volume mounted at runtime)
# or /opt/maestro (managed by ORCE). A staging dir lets us copy at startup.
# BUILD_LIBRDKAFKA=0 tells node-rdkafka to use the system librdkafka
# instead of downloading and compiling its own copy.
RUN mkdir -p /opt/rdkafka-staging && \
    cd /opt/rdkafka-staging && \
    npm init -y && \
    BUILD_LIBRDKAFKA=0 npm install node-red-contrib-rdkafka

# Patched rdkafka.js with SSL/mTLS support for cluster Kafka connections.
COPY rdkafka-patch.js /opt/rdkafka-staging/rdkafka-patch.js

# ── GUI Generator (JSON Forms) ──────────────────────────────────────
# Install JSON Forms packages and the Node-RED UI builder into a staging
# directory. JSON Forms renders dynamic UIs from JSON Schema + UI Schema
# definitions — used for the DCM catalogue interface.
# Reference: https://jsonforms.io/
RUN mkdir -p /opt/jsonforms-staging && \
    cd /opt/jsonforms-staging && \
    npm init -y && \
    npm install \
        @jsonforms/core \
        @jsonforms/react \
        @jsonforms/material-renderers \
        @mui/material \
        @mui/icons-material \
        @emotion/react \
        @emotion/styled \
        node-red-contrib-uibuilder

# ── Custom entrypoint ───────────────────────────────────────────────
# Copies rdkafka + jsonforms into /data/node_modules at startup,
# applies SSL patch, then delegates to the original ORCE entrypoint.
COPY entrypoint.sh /usr/local/bin/entrypoint-rdkafka.sh
RUN chmod +x /usr/local/bin/entrypoint-rdkafka.sh

ENTRYPOINT ["/usr/local/bin/entrypoint-rdkafka.sh"]

# Do NOT switch to node-red here — the original ORCE entrypoint runs as root
# and handles the user switch internally (run_as_node_red / su-exec).
