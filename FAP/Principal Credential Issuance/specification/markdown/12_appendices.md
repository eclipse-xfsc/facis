[← Validation & Acceptance Criteria](11_validation_acceptance_criteria.md) · [↑ Table of Contents](../README.md)

---

## 12. Appendices

### Appendix A: Glossary

<p align="center"><em>Table 6 Glossary</em></p>

|Term|Category|Definition|Relevant specifications/links|
|---|---|---|---|
|DID (Decentralized Identifier)|SSI building block|Globally unique identifiers that do not depend on a central authority and can be cryptographically resolved|W3C DID Core: https://www.w3.org/TR/didcore/<br><br>|
|Eclipse XFSC (Cross Federation Services Components)|Software framework / component set|An open-source software toolbox for building and operating federated data ecosystems. It provides microservices for identity/trust, credential management, cataloging, and interoperability across federations. Originally part of Gaia-X and now under the Eclipse Foundation. ([projects.eclipse.org][1])|Eclipse XFSC project: https://github.com/eclipse-xfsc<br><br> Eclipse XFSC on Eclipse.org: https://projects.eclipse.org/projects/technology.xfsc<br><br> Eclipse XFSC documentation: https://github.com/eclipsexfsc/docs<br><br>|
|ETSI TS 119 471|Standard|Electronic Signatures and Trust Infrastructures (ESI); Profiles for Electronic Attestation of Attributes; Part 1: General requirements|https://www.etsi.org/deliver/etsi_ts/119400_119499/119471/01.01.01_60/ts_119471v010101p.pdf<br><br>|
|ETSI TS 119 472-1|Standard|Electronic Signatures and Trust Infrastructures (ESI); Profiles for Electronic Attestation of Attributes; Part 1: General requirements|https://www.etsi.org/deliver/etsi_ts/119400_119499/11947201/01.01.01_60/ts_11947201v010101p.pdf<br><br>|
|European Cybersecurity Group|Standard|The European Cybersecurity Certification Group was established to help ensure the consistent implementation and application of the Cybersecurity Act.|https://digitalstrategy.ec.europa.eu/en/policies/cybersecurity-certificationgroup<br><br>|
|OpenID4VC (OpenID for Verifiable Credentials)|Protocol framework|OpenID Foundation specs that define how verifiable credentials are issued and presented using OAuth2/OIDC flows|OpenID4VCI: https://openid.net/specs/openid-4-verifiable-credentialissuance-1_0.html<br><br>OpenID4VP: https://openid.net/specs/openid-4-verifiable-presentations1_0.html<br><br>|
|OpenID4VCI (credential issuance)|Protocol|OAuth2/OpenID-based flows for issuing verifiable credentials from an issuer to a wallet|OAuth 2.0 RFC 6749: https://www.rfceditor.org/rfc/rfc6749<br><br> PKCE RFC 7636: https://www.rfceditor.org/rfc/rfc7636<br><br> OpenID: https://openid.net/specs/openid-4-verifiable-credentialissuance-1_0-ID1.html<br><br>|
|Organization Credential Manager (OCM)|XFSC component|Manages digital credentials for organizations in SSIbased ecosystems (e.g., connections, DID management, credential issuance/verification)|https://github.com/eclipsexfsc/docs/tree/main/ocm-wstack<br><br>|
|Personal Credential Manager (PCM)|XFSC component|Client-side service that holds user credentials and enables selective disclosure and interaction in SSI contexts. ([projects.eclipse.org][1])|https://github.com/eclipsexfsc/docs/tree/main/pcmcloud<br><br>|
|SD-JWT|Standard|Selective Disclosure JWT|https://datatracker.ietf.org/doc/rfc9901/<br><br>|
|SSI (SelfSovereign Identity)|Identity paradigm|Decentralized model where users control identities and credentials using cryptography, DIDs, and VCs. ([GXFS.eu][6])|W3C DID Core: https://www.w3.org/TR/didcore/<br><br> W3C Verifiable Credentials: https://www.w3.org/TR/vcdata-model/<br><br>|
|Token Status List|Standard|Token Status List describes how to embed information for revocation in SD-JWT tokens or W3C Credentials|https://www.ietf.org/archive/id/draft-ietf-oauth-status-list02.html https://github.com/eclipsexfsc/statuslist-service<br><br>|
|Trust Services API (TSA)|XFSC component|Provides trust validation, policy enforcement, and cryptographic verification across ecosystem participants. ([eclipse.dev][5])|https://github.com/eclipsexfsc/docs/tree/main/tsa<br><br>|
|VC (Verifiable Credential)|SSI data model|Cryptographically secure, machine-verifiable statements about a subject that can be selectively disclosed|W3C VC Data Model: https://www.w3.org/TR/vcdata-model/<br><br>|
|Orchestration Engine (ORCE)|Framework|XFSC orchestration engine based on Node Red|https://github.com/eclipsexfsc/orchestration-engine<br><br>|
|Issuer|SSI role|Entity that creates and signs VCs asserting attributes about a subject|W3C VC Data Model: https://www.w3.org/TR/vcdata-model/<br><br>|
|Holder|SSI role|Entity (often the user) storing and presenting credentials|W3C VC Data Model: https://www.w3.org/TR/vcdata-model/<br><br>|
|Verifier|SSI role|Entity that requests and verifies credentials/presentations|OpenID4VP: https://openid.net/specs/openid-4-verifiable-presentations1_0.html|


### Appendix B: Tenant-specific Ingress Rule
```yaml
apiVersion: networking.k8s.io/v1 
kind: Ingress 
metadata:
    name: {{ .Release.Name }}-diddocument-ingress 
    annotations:

        cert-manager.io/cluster-issuer: letsencrypt-prod 
        nginx.ingress.kubernetes.io/configuration-snippet: |
            proxy_set_header X-DID did:web:{{ .Values.ingress.hostname }};
            proxy_set_header X-NAMESPACE {{ .Values.ingress.tenantName }};

        nginx.ingress.kubernetes.io/rewrite-target: /v1/did/document

spec: 
    ingressClassName: nginx 
    rules:

    - host: {{ .Values.ingress.hostname }} http: 
    paths:

    - path: /.well-known/did.json 
    pathType: ImplementationSpecific 
    backend:

        service: 
            name: {{ .Values.ingress.service.backend }} 
            port:
                number: {{ .Values.ingress.service.port }} 
{{ if .Values.ingress.tls }} 
tls:
- hosts:
    - {{ .Values.ingress.hostname }}

  secretName: {{ .Values.ingress.tls.secret }} 
{{ end }}
```
---

[← Validation & Acceptance Criteria](11_validation_acceptance_criteria.md) · [↑ Table of Contents](../README.md)

