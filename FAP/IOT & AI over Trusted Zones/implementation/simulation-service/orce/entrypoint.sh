#!/usr/bin/env bash
set -Eeuo pipefail

# Copy node-red-contrib-rdkafka into /data/node_modules so that Node-RED
# (userDir=/data) can find the rdkafka-broker and rdkafka-producer node types.
# The module is pre-built during docker build in /opt/rdkafka-staging.
STAGING="/opt/rdkafka-staging/node_modules"
TARGET="/data/node_modules"

if [ -d "${STAGING}/node-red-contrib-rdkafka" ]; then
    mkdir -p "${TARGET}"

    # Copy rdkafka and its native dependencies
    for pkg in node-red-contrib-rdkafka node-rdkafka bindings file-uri-to-path nan; do
        if [ -d "${STAGING}/${pkg}" ]; then
            rm -rf "${TARGET}/${pkg}"
            cp -a "${STAGING}/${pkg}" "${TARGET}/${pkg}"
        fi
    done

    # Apply SSL patch — replaces the original rdkafka.js with our version
    # that supports security.protocol=ssl + cert paths in the broker config
    if [ -f /opt/rdkafka-staging/rdkafka-patch.js ]; then
        cp /opt/rdkafka-staging/rdkafka-patch.js "${TARGET}/node-red-contrib-rdkafka/rdkafka/rdkafka.js"
        echo "[entrypoint-rdkafka] Applied SSL patch to rdkafka.js"
    fi

    # Node-RED only loads modules listed in /data/package.json
    if [ -f /data/package.json ]; then
        node -e "
            const fs = require('fs');
            const pkg = JSON.parse(fs.readFileSync('/data/package.json', 'utf8'));
            if (!pkg.dependencies) pkg.dependencies = {};
            if (!pkg.dependencies['node-red-contrib-rdkafka']) {
                pkg.dependencies['node-red-contrib-rdkafka'] = '*';
                fs.writeFileSync('/data/package.json', JSON.stringify(pkg, null, 4) + '\n');
                console.log('[entrypoint-rdkafka] Added node-red-contrib-rdkafka to /data/package.json');
            }
        "
    fi

    chown -R node-red:node-red "${TARGET}" 2>/dev/null || true
    echo "[entrypoint-rdkafka] rdkafka modules ready in ${TARGET}"
fi

# Delegate to the original ORCE entrypoint
exec /usr/src/node-red/entrypoint.sh "$@"
