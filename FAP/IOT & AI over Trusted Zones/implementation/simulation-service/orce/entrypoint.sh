#!/usr/bin/env bash
set -Eeuo pipefail

TARGET="/data/node_modules"
mkdir -p "${TARGET}"

# ── 0. Bootstrap /data from the ORCE image if empty (first boot) ────
# The ORCE image keeps its defaults in /home/user/.node-red/ but the
# runtime uses --userDir /data/. On first boot (empty PVC) we need to
# seed /data/ with settings.js, package.json, and the default flows.
if [ ! -f /data/settings.js ]; then
    ORCE_HOME="/opt/maestro/MBE/.node-red"
    echo "[entrypoint] First boot — seeding /data/ from ORCE defaults (${ORCE_HOME})"

    if [ -d "${ORCE_HOME}" ]; then
        # Copy ALL ORCE files: settings, flows, guided CSS/JS (branding, dark mode,
        # AI button, zoom), config files, and the default package.json.
        # This is what makes it ORCE rather than plain Node-RED.
        for f in $(ls -1A "${ORCE_HOME}/" 2>/dev/null); do
            # Skip node_modules — we manage those separately via staging dirs
            if [ "${f}" = "node_modules" ]; then
                continue
            fi
            if [ ! -e "/data/${f}" ]; then
                cp -a "${ORCE_HOME}/${f}" "/data/${f}"
                echo "[entrypoint]   copied ${f}"
            fi
        done
    else
        # Fallback: try /home/user/.node-red (older ORCE image layout)
        echo "[entrypoint] WARN: ${ORCE_HOME} not found, trying /home/user/.node-red/"
        for f in settings.js package.json flows.json flows_cred.json .config.nodes.json; do
            if [ -f "/home/user/.node-red/${f}" ]; then
                cp "/home/user/.node-red/${f}" "/data/${f}"
                echo "[entrypoint]   copied ${f}"
            fi
        done
    fi

    chown -R node-red:node-red /data/ 2>/dev/null || true
fi

# ── 1. Kafka plugin (rdkafka) ────────────────────────────────────────
# Copy node-red-contrib-rdkafka into /data/node_modules so that Node-RED
# (userDir=/data) can find the rdkafka-broker and rdkafka-producer node types.
# The module is pre-built during docker build in /opt/rdkafka-staging.
RDKAFKA_STAGING="/opt/rdkafka-staging/node_modules"

if [ -d "${RDKAFKA_STAGING}/node-red-contrib-rdkafka" ]; then
    # Copy rdkafka and its native dependencies
    for pkg in node-red-contrib-rdkafka node-rdkafka bindings file-uri-to-path nan; do
        if [ -d "${RDKAFKA_STAGING}/${pkg}" ]; then
            rm -rf "${TARGET}/${pkg}"
            cp -a "${RDKAFKA_STAGING}/${pkg}" "${TARGET}/${pkg}"
        fi
    done

    # Apply SSL patch — replaces the original rdkafka.js with our version
    # that supports security.protocol=ssl + cert paths in the broker config
    if [ -f /opt/rdkafka-staging/rdkafka-patch.js ]; then
        cp /opt/rdkafka-staging/rdkafka-patch.js "${TARGET}/node-red-contrib-rdkafka/rdkafka/rdkafka.js"
        echo "[entrypoint] Applied SSL patch to rdkafka.js"
    fi

    echo "[entrypoint] rdkafka modules ready"
fi

# ── 2. GUI Generator (JSON Forms + uibuilder) ───────────────────────
# Copy JSON Forms packages and node-red-contrib-uibuilder into /data/node_modules
# so the GUI Generator can render dynamic UIs from JSON Schema + UI Schema.
JSONFORMS_STAGING="/opt/jsonforms-staging/node_modules"

if [ -d "${JSONFORMS_STAGING}/node-red-contrib-uibuilder" ]; then
    # Copy uibuilder and all JSON Forms / MUI dependencies
    for pkg in $(ls -1 "${JSONFORMS_STAGING}/" 2>/dev/null); do
        if [ -d "${JSONFORMS_STAGING}/${pkg}" ] && [ ! -d "${TARGET}/${pkg}" ]; then
            cp -a "${JSONFORMS_STAGING}/${pkg}" "${TARGET}/${pkg}"
        fi
    done
    # Handle scoped packages (@jsonforms, @mui, @emotion)
    for scope in @jsonforms @mui @emotion; do
        if [ -d "${JSONFORMS_STAGING}/${scope}" ]; then
            mkdir -p "${TARGET}/${scope}"
            for pkg in $(ls -1 "${JSONFORMS_STAGING}/${scope}/" 2>/dev/null); do
                rm -rf "${TARGET}/${scope}/${pkg}"
                cp -a "${JSONFORMS_STAGING}/${scope}/${pkg}" "${TARGET}/${scope}/${pkg}"
            done
        fi
    done

    echo "[entrypoint] JSON Forms + uibuilder modules ready"
fi

# ── 3. Register modules in /data/package.json ────────────────────────
# Node-RED only loads modules listed in /data/package.json
if [ -f /data/package.json ]; then
    node -e "
        const fs = require('fs');
        const pkg = JSON.parse(fs.readFileSync('/data/package.json', 'utf8'));
        if (!pkg.dependencies) pkg.dependencies = {};
        let changed = false;
        const deps = {
            'node-red-contrib-rdkafka': '*',
            'node-red-contrib-uibuilder': '*'
        };
        for (const [name, ver] of Object.entries(deps)) {
            if (!pkg.dependencies[name]) {
                pkg.dependencies[name] = ver;
                changed = true;
                console.log('[entrypoint] Added ' + name + ' to /data/package.json');
            }
        }
        if (changed) {
            fs.writeFileSync('/data/package.json', JSON.stringify(pkg, null, 4) + '\n');
        }
    "
fi

# ── 4. Fix ownership ────────────────────────────────────────────────
chown -R node-red:node-red "${TARGET}" 2>/dev/null || true

# ── 5. Delegate to the original ORCE entrypoint ─────────────────────
exec /usr/src/node-red/entrypoint.sh "$@"
