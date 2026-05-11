[← Security & Trust](08_security_trust.md) · [↑ Table of Contents](README.md) · [Standards & Protocols →](10_standards_protocols.md)

---

## 9. Deployment & Operations



### 9.1 Deployment

#### [FR-PCI-49] Deployment Playbook   
**Priority:** MUST   
**Description:** The deployment MUST be reproducible in other Kubernetes environments. The setup MUST be executable over any generic mechanism. For instance, scripts, terraform, ansible, Kubernetes operators or similar.   
**Acceptance criteria:**   
Demonstration of automatic setup in a second cluster.

#### [FR-PCI-50] Route Management   
**Priority:** MUST   
**Description:** For each issuance workflow, there MUST be appropriate route management within ingresses which separates the tenants from each other. This includes tenant headers for OCM W-Stack and [others](https://github.com/eclipse-xfsc/deployment/blob/main/OCM%20W-Stack/Well%20Known%20Ingress%20Rules/templates/ingress.yaml#L9) (see Appendix B).
**Acceptance criteria:**   
Code review

#### [FR-PCI-51] Deployment Publication   
**Priority:** MUST   
**Description:** All scripts and deployment helm charts MUST be integrated into the [XFSC deployment repository](https://github.com/eclipse-xfsc/deployment).   
**Acceptance criteria:**   
Pull Requests created and merged by maintainer according to milestones.

#### [FR-PCI-52] Deployment Tool Stack   
**Priority:** MUST   
**Description:** The deployment tool stack MUST be open-source to avoid technology lock-in for users. The tools used for deployment MAY be ORCE, Ansible, Terraform, Crossplane or similar standard tools which simplify the setup of the solution.   
**Acceptance criteria:**   
Presentation of choice and documentation.

#### [FR-PCI-53] Resource Limitation   
**Priority:** MUST   
**Description:** All helm charts and templates MUST be limited to consumed resources. Setup resource limitations (scale out or scale downs) MAY be realized over dynamic processes/additional tooling like KEDA or any other tool stack.   
**Acceptance criteria:**
 - Documentation on how to set a limit,
- Documentation on how to scale down and scale up.


#### [FR-PCI-54] Web Documentation    
**Priority:** MUST   
**Description:** The documentation for the deployment MUST be created on GitHub. Additionally, there MUST be a web-formatted GitHub support page where the documentation is rendered in a way that people can search for FAQ, deployment topics and guides over GitHub Pages. The page can be rendered out of the existing documentation, but it MUST contain well-formatted hints, FAQs, and other helpful things for setting up the deployment.   
**Acceptance criteria:**   
Presentation of the support page for deployment.


#### 9.2 Operational Requirements

#### [FR-PCI-55] Jaeger Tracing   
**Priority:** MUST   
**Description:** The solution MUST provide a pre-configured Jaeger instance for tracing events in its deployment.   
**Acceptance criteria:**
- Documentation,
- Presentation of demo logs.


#### [FR-PCI-56] Prometheus   
**Priority:** MUST   
**Description:** The solution MUST provide Prometheus Instances to collect metrics.  
**Acceptance criteria:**
 - Documentation,
- Presentation of demo logs.


#### [FR-PCI-57] OTEL Collection   
**Priority:** MUST   
**Description:** The solution MUST provide an OTEL Collector with interfaces to Prometheus and Jaeger.   
**Acceptance criteria:** Demonstration of working logging.

#### [FR-PCI-58] Health Endpoints/Logging   
**Priority:** MUST   
**Description:** The solution MUST provide health endpoints to reflect the status of the application and appropriate logging.  
**Acceptance criteria:**   
Demo logs of Kubernetes.

---

[← Security & Trust](08_security_trust.md) · [↑ Table of Contents](README.md) · [Standards & Protocols →](10_standards_protocols.md)

