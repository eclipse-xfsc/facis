[← Standards & Protocols](10_standards_protocols.md) · [↑ Table of Contents](README.md) · [Appendices →](12_appendices.md)

---

## 11. Validation & Acceptance Criteria

Besides the technical acceptance criteria in the requirements, there are more validation rules and top-level acceptance criteria which MUST be fulfilled during acceptance presentations milestone by milestone. All these criteria MUST be implemented as well via the BDD Executor as BDD test steps. In general, it MUST also be clarified which parts of the implementation are performed by AI and how this affects code quality and project performance.

### 11.1 Tenant Management Milestone

<p align="center"><em>Table 1 Tenant Management Milestone</em></p>

|No.|Validation criteria|Definition of done|
|---|---|---|
|FR&#8209;PCI&#8209;65|Tenant can be registered|A tenant can be registered, activated per email and confirmed by the provider tenant administration. The tenant is visible in the tenant listing.|
|FR&#8209;PCI&#8209;66|Tenant can be deleted|The tenant can be deleted by the tenant administrator (provider and participant). All resources in the cluster are deleted. A confirmation was triggered.|
|FR&#8209;PCI&#8209;67|Tenant can be confirmed|After registration the provider tenant admin must be able to confirm a registration by reviewing the application details. All resources will be provided afterwards.|
|FR&#8209;PCI&#8209;68|Tenant can be rejected|After registration, the provider tenant admin must be able to reject a registration by reviewing the application details. An email is sent out. No resources are provided.|
|FR&#8209;PCI&#8209;69|Configured participant login works|After the participant IAM system was configured by the participant tenant admin, the login for the issuer page works with the principal credentials.|
|FR&#8209;PCI&#8209;70|Multiple tenants can be created|Multiple tenants under multiple domains/routes can be created and work properly from landing page to authentication.|
|FR&#8209;PCI&#8209;71|Tenants can be customized with layouts, logos, and custom texts for landing page|After tenant creation, each tenant landing page must be configurable (e.g., logos, styles, custom texts of the participant).|
|FR&#8209;PCI&#8209;72|Issuer management can be delegated|Within the tenant administration, roles or user accounts can be unlocked for issuer management.|
|FR&#8209;PCI&#8209;73|Eclipse IP scans|Eclipse IP scans are integrated and triggered, no license conflicts with Eclipse license. compatibility (e.g., no GPL, GPL 2, AGPL, LGPL).|
|FR&#8209;PCI&#8209;74|Deployment integration|All scripts and changes are available as PRs in the XFSC deployment repository.|
|FR&#8209;PCI&#8209;75|Version tagging|Running version tagged and documented.|


### 11.2 Issuer Management Milestone

<p align="center"><em>Table 2 Issuer Management Milestone</em></p>

|No.|Validation criteria|Definition of done|
|---|---|---|
|FR&#8209;PCI&#8209;76|Credential configuration can be created|Any delegated user can create a credential configuration by configuring fields, background image, description etc. according to the OID4VCI metadata specification.|
|FR&#8209;PCI&#8209;77|Credential configuration can be modified|An existing credential configuration can be modified by changing the background images, changing texts, claims etc.|
|FR&#8209;PCI&#8209;78|Credential configuration can be deleted|An existing credential configuration can be deleted, but existing credentials remain resolvable.|
|FR&#8209;PCI&#8209;79|Credential logo can be configured|Logo images can be uploaded for a credential configuration. The image size is optimized and/or highlighted and the image resolvable over the well-known openID issuer configuration.|
|FR&#8209;PCI&#8209;80|Flow per credential configuration can be configured|For each credential configuration, a custom flow consisting of multiple page steps and layouts (e.g., survey, data protection information, introduction of process, QR code page) can be created.|
|FR&#8209;PCI&#8209;81|History per configuration shows latest issuances and status|A credential configuration shows a list of credential history events with ID of the credential. The ID can be searched, and the credential can be revoked.|
|FR&#8209;PCI&#8209;82|Issuance based on participant backend|The credential must be issued over the usage of the participant signing and credential creation capabilities.|
|FR&#8209;PCI&#8209;83|Issuance based on participant data repository|The credential must be issued over the usage of the participant data repository and internal signing capabilities.|
|FR&#8209;PCI&#8209;84|Eclipse IP scans|Eclipse IP scans are integrated and triggered, no license conflicts with Eclipse license compatibility (e.g., no GPL, GPL 2, AGPL, LGPL).|
|FR&#8209;PCI&#8209;85|Deployment integration|All scripts and changes are available as PRs in the XFSC deployment repository.|
|FR&#8209;PCI&#8209;86|Version tagging|Running version tagged and documented.|


### 11.3 E2E Issuance Milestone

<p align="center"><em>Table 3 E2E Issuance Milestone</em></p>

|No.|Validation criteria|Definition of done|
|---|---|---|
|FR&#8209;PCI&#8209;87|Multiple issuance flows can be used|Multiple issuance flows in various layouts can be used, and credentials can be imported in PCM Mobile.|
|FR&#8209;PCI&#8209;88|Multiple tenants and users can be used|Multiple tenants and users can be used for various issuances in the PCM mobile app.|
|FR&#8209;PCI&#8209;89|Version tagging|Running version tagged and documented.|
|FR&#8209;PCI&#8209;90|Eclipse IP scans|Eclipse IP scans are integrated and triggered, no license conflicts with Eclipse license compatibility (e.g., no GPL, GPL 2, AGPL, LGPL).|


### 11.4 Second Cluster Deployment Milestone

<p align="center"><em>Table 4 Second Cluster Deployment Milestone</em></p>


|No.|Validation criteria|Definition of done|
|---|---|---|
|FR&#8209;PCI&#8209;91|Solution is deployed on a second cluster|E2E credential issuance works.|
|FR&#8209;PCI&#8209;92|Deployment integration|All scripts and changes are available as PRs in the XFSC deployment repository.|
|FR&#8209;PCI&#8209;93|Version tagging|Running version and fixes tagged and documented.|
|FR&#8209;PCI&#8209;94|Eclipse IP scans|Eclipse IP scans are integrated and triggered, no license conflicts with Eclipse license compatibility (e.g., no GPL, GPL 2, AGPL, LGPL).|


### 11.5 GitHub Finalization Milestone

<p align="center"><em>Table 5 GitHub Finalization Milestone</em></p>

|No.|Validation criteria|Definition of done|
|---|---|---|
|FR&#8209;PCI&#8209;95|Version tagging|All repositories are tagged with the latest versions. Releases are created. Helm charts and Docker Images are uploaded in Harbor in the latest versions.|
|FR&#8209;PCI&#8209;96|Documentation|Documentation feedback is refined in the GitHub readmes. All readmes are up to date.|
|FR&#8209;PCI&#8209;97|Eclipse IP scans|Eclipse IP scans are integrated and triggered, no license conflicts with Eclipse license compatibility (e.g., no GPL, GPL 2, AGPL, LGPL etc.).|
|FR&#8209;PCI&#8209;98|EUDI compliance statement|The solution contains documentation describing which parts must be modified and/or developed to reach EUDI and ARF compliance in later versions of the solution.|
|FR&#8209;PCI&#8209;99|No open PRs and issues|All GitHub repositories for the solution have no open issues/no open PRs.|
|FR&#8209;PCI&#8209;100|Standard workflows integrated|All standard workflows in GitHub are integrated (Docker, Helm, Eclipse scan, test).|
|FR&#8209;PCI&#8209;101|Successful workflow runs|All workflow runs must be successful without any error.|

---

[← Standards & Protocols](10_standards_protocols.md) · [↑ Table of Contents](README.md) · [Appendices →](12_appendices.md)

