// Digital-Contracting-Service.js
module.exports = function (RED) {
    const { exec } = require('child_process');
    const fs = require('fs');
    const tmp = require('tmp');
    const path = require('path');
    const request = require('request');

    function DeployNode(config) {
        RED.nodes.createNode(this, config);
        const node = this;

        const kubeContent = config.kubeconfigContent;
        const keyContent = config.privateKeyContent;
        const crtContent = config.certificateContent;
        const clientId = config.clientId || 'digital-contracting-service';
        const domain = config.domainAddress;
        const urlPath = config.instanceName;
        const keycloakUrl = config.keycloakUrl;
        const realm = config.realm || 'gaia-x';
        const adminUser = config.adminUser;
        const adminPass = config.adminPass;
        const newUser = config.newUser;
        const newPass = config.newPass;
        const clientRole = config.clientRole || 'digital-contracting-service-user';

        let storedClientSecret = null;

        function writeTempFiles() {
            const kubeTmp = tmp.fileSync({ prefix: 'kube-', postfix: '.yaml' });
            fs.writeFileSync(kubeTmp.name, kubeContent);
            const keyTmp = tmp.fileSync({ prefix: 'key-', postfix: '.key' });
            fs.writeFileSync(keyTmp.name, keyContent);
            const crtTmp = tmp.fileSync({ prefix: 'crt-', postfix: '.crt' });
            fs.writeFileSync(crtTmp.name, crtContent);
            return { kubeTmp, keyTmp, crtTmp };
        }

        function getAdminToken(callback) {
            const tokenUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/token`;
            request.post({
                url: tokenUrl,
                form: { client_id: 'admin-cli', username: adminUser, password: adminPass, grant_type: 'password' },
                json: true,
                strictSSL: false
            }, (err, resp, body) => {
                if (err || resp.statusCode !== 200) {
                    return callback(new Error(`Admin token error: ${err || JSON.stringify(body)}`));
                }
                callback(null, body.access_token);
            });
        }

        function getApiToken(msg, callback) {
            const tokenUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/token`;
            const secret = msg.clientSecret || storedClientSecret;
            if (!secret) {
                return callback(new Error('clientSecret not available; run deploy first'));
            }
            const form = {
                client_id: clientId,
                client_secret: secret,
                username: msg.username || newUser,
                password: msg.password || newPass,
                grant_type: 'password'
            };
            request.post({ url: tokenUrl, form, json: true, strictSSL: false }, (err, resp, body) => {
                if (err || resp.statusCode !== 200) {
                    return callback(new Error(`API token error: ${err || body.error_description || JSON.stringify(body)}`));
                }
                callback(null, body.access_token);
            });
        }


        node.on('input', function (msg) {

            let kubeTmp, keyTmp, crtTmp;
            try {
                ({ kubeTmp, keyTmp, crtTmp } = writeTempFiles());
            } catch (err) {
                node.error(`Failed to write temp files: ${err.message}`, msg);
                node.status({ fill: 'red', shape: 'ring', text: 'file error' });
                return;
            }
            
            const args = [kubeTmp.name, keyTmp.name, crtTmp.name, domain, urlPath, keycloakUrl, realm, adminUser, adminPass, newUser, newPass, clientRole];
            const deployScript = path.join(__dirname, 'deploy.sh');
            const cmd = `bash ${JSON.stringify(deployScript)} ` + args.map(a => JSON.stringify(a)).join(' ');

            node.log(`Executing: ${cmd}`);
            node.status({ fill: 'blue', shape: 'dot', text: 'deploying' });

            exec(cmd, { cwd: __dirname }, (err, stdout, stderr) => {
                try { kubeTmp.removeCallback(); keyTmp.removeCallback(); crtTmp.removeCallback(); } catch (_) { }
                if (err) {
                    const errorMsg = stderr || err.message;
                    node.error(errorMsg, msg);
                    node.status({ fill: 'red', shape: 'ring', text: 'deploy failed' });
                    msg.payload = errorMsg;
                    node.send(msg);
                    return;
                }

                const res = {};
                stdout.split(/\r?\n/).forEach(line => {
                    let m;
                    if (m = line.match(/^🔹 ingress External-IP: (.+)$/)) res.ingressExternalIp = m[1];
                    else if (m = line.match(/^🔹 Client Secret:\s+(.+?)\s*$/)) res.clientSecret = m[1].trim();
                    else if (m = line.match(/^🔹 DCS URL:\s+(.+)$/)) res.dcsUrl = m[1];
                });

                node.ingressExternalIp = res.ingressExternalIp;
                node.clientSecret = res.clientSecret;
                node.dcsUrl = res.dcsUrl;

                storedClientSecret = res.clientSecret;

                node.log(`Deployment result: ${JSON.stringify(res)}`);
                node.status({ fill: 'green', shape: 'dot', text: 'deployed' });

                msg.payload = res;
                node.send(msg);
            });
        });

        node.on('close', function (removed, done) {
            if (removed) {

                let kubeTmp;
                try {
                    kubeTmp = tmp.fileSync({ prefix: 'kube-', postfix: '.yaml' });
                    fs.writeFileSync(kubeTmp.name, kubeContent);
                } catch (err) {
                    node.warn(`uninstall: failed to write kubeconfig temp file: ${err.message}`);
                    done();
                    return;
                }

                const args = [kubeTmp.name, urlPath];
                const uninstallScript = path.join(__dirname, 'uninstall.sh');
                const cmd = `bash ${JSON.stringify(uninstallScript)} ` + args.map(a => JSON.stringify(a)).join(' ');
                node.log(`🔄 Running uninstall: ${cmd}`);
                exec(cmd, { cwd: __dirname }, (err, stdout, stderr) => {
                    try { kubeTmp.removeCallback(); } catch (_) { }
                    if (err) {
                        node.error(`uninstall failed: ${stderr || err.message}`);
                    } else {
                        node.log(`uninstall output:\n${stdout}`);
                    }
                    done();
                });
            } else {
                done();
            }
        });
    }

    RED.nodes.registerType("Digital-Contracting-Service", DeployNode);
    RED.httpAdmin.get('/digital-contracting-service/info/:id', function (req, res) {
        var nodeId = req.params.id;
        var node = RED.nodes.getNode(nodeId);
        if (!node) {
            return res.status(404).send({ error: "Node not found" });
        }

        var cfg = {
            ingressExternalIp: node.ingressExternalIp || "",
            dcsUrl: node.dcsUrl || "",
            clientSecret: node.clientSecret || ""
        };
        res.json(cfg);
    });
};
