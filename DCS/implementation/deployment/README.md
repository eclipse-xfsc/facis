[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)

# Digital Contracting Service

An automated orchestration workspace that deploys a [Digital Contracting Service](https://github.com/eclipse-xfsc/facis/tree/main/DCS) instance to a Kubernetes cluster.

---

## 🚀 Overview

The Digital Contracting Service (DCS) provides an open-source platform for creating, signing, and managing contracts digitally.
Integrated with the European Digital Identity Wallet (EUDI), it guarantees that all digital transactions are secure, legally binding, and interoperable.
DCS allows organizations to streamline business processes, reduce paperwork, and ensure compliance with eIDAS 2.0 regulations, while fostering trust across federated partners.

Key components of the Digital Contracting Service include:
- Multi-Contract Signing: Enables multi-party contract execution within a single integrated workflow.
- Automated Workflows: Automates contract generation, execution, and deployment to ensure legal
consistency and efficiency.
- Lifecycle Management: Monitors contracts with alerts for renewals, expirations, or required actions.
- Signature Management: Links contract signatures to verifiable digital identities to maintain legal validity
and trust.
- Secure Archiving: Stores signed contracts in a tamper-evident archive compliant with retention policies.
- Machine Signing: Supports automated signing for high-volume or routine transactions.

This module allows you to set up and interact with the Digital Contracting Service visually inside the ORCE environment. You don’t need to write any code or handle any complex API integration manually—just install the Node-RED node for Digital Contracting Service, drop it into your flow, and configure the endpoint and query.

Thanks to ORCE’s orchestration features, deploying a Digital Contracting Service instance and querying it happens in just a few clicks. Upload your configs, drag your node, and start the Digital Contracting Service

---

## ⚡️ Click-to-Deploy

---
## 🛠️ How to Use

### 1. Prepare the environment and prerequisites
You'll need:
1.1. A Kubernetes cluster to host the child instances
1.2. A local ORCE as the parent to host the initial developing environment

### 1.1. Kubernetes
"Orchestration Engine" node requires a working Kubernetes cluster with ingress installed on it. Initiate a K8s cluster and install nginx-ingress on it using this command.
```bash
export KUBECONFIG=`<YOUR KUBECONFIG PATH>`
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.3/deploy/static/provider/cloud/deploy.yaml
```
You can learn more by reading the [official documentation](https://kubernetes.github.io/ingress-nginx/deploy/)
After this step, you can proceed to step 1.2 (Installing a local ORCE)

### 1.2. Local ORCE
Install ORCE as described in the [ORCE page](https://github.com/eclipse-xfsc/orchestration-engine):
```bash
docker run -d --name xfsc-orce-instance -p 1880:1880 leanea/facis-xfsc-orce:1.0.16
```
Go to [http://localhost:1880](http://localhost:1880).

### Install Digital Contracting Service Node
Click on "New Node" in the sidebar.

![new button](./docImage/add-new-node.jpg?raw=true)

Upload `node-red-contrib-digital-contracting-service-0.0.1.tgz` from this repository and install. Refresh to activate the node.


### 2. Install your node
click on the "Install" tab. Then on the upload icon.The node will be successfully installed.
![step two (flow)](./docImage/newstep.png?raw=true)


### 3. Create your flow
Drag in an Inject node, the **Digital Contracting Service** node, and a Debug node. Connect them:

![step three (flow)](./docImage/create-your-flow.png?raw=true)


### 4. Name your instance and configure the node
Double-click on the Digital Contracting Service node to open the edit dialog.
In this step, you must choose a **Digital Contracting Service Name**. This will become your instance’s unique identifier, so it must be:
- Unique (not used by any other instance)
- Free of special characters (letters and numbers only)
For example, if you name it `mydcs`, it will be used internally for instance referencing and must remain distinct.
![step four (flow)](./docImage/step2.png?raw=true)


### 5. Provide your kubeconfig file
In this tab, you need to provide the **kubeconfig** file of your target Kubernetes cluster.
This file allows the DCS node to access your Kubernetes environment and deploy the DCS instance correctly.
![step five (flow)](./docImage/step3.png?raw=true)


### 6. Provide domain address and TLS credentials
In this tab, you must enter the **domain address** where the DCS will be accessible. You’ll also need to upload your **TLS certificate** and **private key**.

The final accessible URL is formed by combining this domain with the DCS instance name you set earlier. For example:
- Instance Name: `mydcs`
- Domain: `example.com`
- Resulting URL: `example.com/mydcs`
Make sure your TLS credentials match the provided domain.
![step six (flow)](./docImage/step4.png?raw=true)


### 8. Information tab
After the service is successfully deployed, you can switch to the **Information** tab.
Here, the final URL of your deployed catalogue instance will be shown—ready to be copied and used for access or integration.
Click **Done** and then **Deploy**. Activate the Inject node.
![step eight (flow)](./docImage/step7.png?raw=true)
You should see JSON output in the Debug panel, showing catalogue entries.

---

## ⚙️ Configuration

Before running:

1. **DCS URL**  
   Set the URL of your DCS instance.

2. **Query Parameters**  
   Provide any filters or search strings in the node editor or in `msg.payload`.

3. **Authorization Token (optional)**  
   The DCS endpoints require auth headers (Bearer token).

---

## 📁 Directory Contents
```
.
├── node-red-contrib-digital-contracting-service-0.0.1.tgz
├── DigitalContractingService.html
├── DigitalContractingService.js
├── package.json
```

- **node-red-contrib-digital-contracting-service-0.0.1.tgz**  
  Installable node package.

- **DigitalContractingService.html**  
  Node-RED UI form.

- **DigitalContractingService.js**  
  Backend logic to send API requests and return results.

- **package.json**  
  Metadata and dependencies.

---

## 📦 Dependencies

```json
"node": ">=14.0.0",
"node-red": ">=3.0.0"
```

---

## 🔗 Links & References

- [Digital Contracting Service - XFSC](https://github.com/eclipse-xfsc/facis/tree/main/DCS)


---

## 📝 License

This project is licensed under the Apache License 2.0. See the [LICENSE](../LICENSE) file for details.
