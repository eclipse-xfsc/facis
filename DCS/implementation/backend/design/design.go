package design

import (
	. "goa.design/goa/v3/dsl"
)

// API root
var _ = API("dcs", func() {
	Title("DCS API Server")
	Version("0.0.1")

	Server("dcs", func() {
		Host("local", func() {
			URI("http://0.0.0.0:8991")
		})
	})
})

// Template Repository Service  (/template/...)
var _template_repository = Service("template_repository", func() {
	Description("Template Repository APIs (/template/...)")

	// POST /template/create
	Method("create", func() {
		Description("Create a new template.")
		Meta("dcs:requirements", "DCS-IR-TR-01")
		Meta("dcs:roles", "Template Creator")
		Meta("dcs:tr:components", "Single- or multi-tiered template generation")
		Meta("dcs:ui", "Template Builder")

		HTTP(func() {
			POST("/template/create")
			Response(StatusOK)
		})

		Result(String)
	})

	// POST /template/submit
	Method("submit", func() {
		Description(`with action flag { forwardTo: "approval" | "draft" } and optional reviewComments. allow resubmission path with approver comments.`)
		Meta("dcs:requirements", "DCS-IR-TR-03", "DCS-IR-TR-04", "DCS-IR-TR-05")
		Meta("dcs:roles", "Template Creator", "Template Reviewer", "Template Approver")
		Meta("dcs:tr:components", "Single- or multi-tiered template generation")
		Meta("dcs:ui", "Template Builder, Template Review, Template Approver")

		HTTP(func() {
			POST("/template/submit")
			Response(StatusOK)
		})

		Result(String)
	})

	// PUT /template/update
	Method("update", func() {
		Description("persist reviewer edits (metadata/clauses/semantics).")
		Meta("dcs:requirements", "DCS-IR-TR-03")
		Meta("dcs:roles", "Template Creator", "Template Reviewer")
		Meta("dcs:tr:components", "Template Versioning")
		Meta("dcs:ui", "Template Builder, Template Review")

		HTTP(func() {
			PUT("/template/update")
			Response(StatusOK)
		})

		Result(Int)
	})

	// POST /template/update
	Method("update_manage", func() {
		Description("update metadata or status.")
		Meta("dcs:requirements", "DCS-IR-TR-07")
		Meta("dcs:roles", "Template Manager")
		Meta("dcs:tr:components", "Template Versioning")
		Meta("dcs:ui", "Template Management Dashboard")

		HTTP(func() {
			POST("/template/update")
			Response(StatusOK)
		})

		Result(Int)
	})

	// GET /template/search
	Method("search", func() {
		Description("perform filtered searches.")
		Meta("dcs:requirements", "DCS-IR-TR-02", "DCS-IR-TR-07")
		Meta("dcs:roles", "Template Creator", "Template Manager")
		Meta("dcs:tr:components", "Search Capabilities")
		Meta("dcs:ui", "Template Builder, Template Management Dashboard")

		HTTP(func() {
			GET("/template/search")
			Response(StatusOK)
		})

		Result(ArrayOf(Any))
	})

	// GET /template/retrieve
	Method("retrieve", func() {
		Description("load submitted template and history/provenance summary. fetch reviewed template with metadata, review history, and validation results. fetch all template entries for dashboard view.")
		Meta("dcs:requirements", "DCS-IR-TR-02", "DCS-IR-TR-03", "DCS-IR-TR-05", "DCS-IR-TR-08")
		Meta("dcs:roles", "Template Reviewer", "Template Approver", "Template Manager")
		Meta("dcs:tr:components", "Template Versioning")
		Meta("dcs:ui", "Template Builder, Template Approver, Template Management Dashboard")

		HTTP(func() {
			GET("/template/retrieve")
			Response(StatusOK)
		})

		Result(Any)
	})

	// GET /template/retrieve/{template_id}
	Method("retrieve_by_id", func() {
		Description("Retrieve a template by template id.")
		Meta("dcs:requirements", "DCS-IR-TR-02", "DCS-IR-TR-03", "DCS-FR-TR-19")
		Meta("dcs:roles", "Template Reviewer", "Template Approver", "Template Manager")
		Meta("dcs:tr:components", "Template Versioning")
		Meta("dcs:ui", "Template Builder, Template Approver, Template Management Dashboard")

		Payload(func() {
			Attribute("template_id", String, "Template ID")
			Required("template_id")
		})

		HTTP(func() {
			GET("/template/retrieve/{template_id}")
			Param("template_id")
			Response(StatusOK)
		})

		Result(Any)
	})

	// POST /template/verify
	Method("verify", func() {
		Description("run policy, schema, and semantic validations; return findings.")
		Meta("dcs:requirements", "DCS-IR-TR-03")
		Meta("dcs:roles", "Template Reviewer")
		Meta("dcs:tr:components", "Semantic Hub")
		Meta("dcs:ui", "Template Review")

		HTTP(func() {
			POST("/template/verify")
			Response(StatusOK)
		})

		Result(Any)
	})

	// POST /template/approve
	Method("approve", func() {
		Description("mark template as approved, with optional decision notes.")
		Meta("dcs:requirements", "DCS-IR-TR-05", "DCS-IR-TR-06")
		Meta("dcs:roles", "Template Approver")
		Meta("dcs:tr:components", "Template Versioning")
		Meta("dcs:ui", "Template Approver")

		HTTP(func() {
			POST("/template/approve")
			Response(StatusOK)
		})

		Result(Int)
	})

	// POST /template/reject
	Method("reject", func() {
		Description("mark template as rejected, requiring reason field.")
		Meta("dcs:requirements", "DCS-IR-TR-05")
		Meta("dcs:roles", "Template Approver")
		Meta("dcs:tr:components", "")
		Meta("dcs:ui", "Template Approver")

		HTTP(func() {
			POST("/template/reject")
			Response(StatusOK)
		})

		Result(Int)
	})

	// POST /template/register
	Method("register", func() {
		Description("register new template into the repository.")
		Meta("dcs:requirements", "DCS-IR-TR-07")
		Meta("dcs:roles", "Template Manager")
		Meta("dcs:tr:components", "Contract Templates Storage & Provenance")
		Meta("dcs:ui", "Template Management Dashboard")

		HTTP(func() {
			POST("/template/register")
			Response(StatusOK)
		})

		Result(Any)
	})

	// POST /template/archive
	Method("archive", func() {
		Description("archive obsolete template.")
		Meta("dcs:requirements", "DCS-IR-TR-07")
		Meta("dcs:roles", "Template Manager")
		Meta("dcs:tr:components", "Contract Templates Storage & Provenance")
		Meta("dcs:ui", "Template Management Dashboard")

		HTTP(func() {
			POST("/template/archive")
			Response(StatusOK)
		})

		Result(Int)
	})

	// GET /template/audit
	Method("audit", func() {
		Description("retrieve audit history of template actions.")
		Meta("dcs:requirements", "DCS-IR-TR-07", "DCS-IR-TR-08")
		Meta("dcs:roles", "Template Manager")
		Meta("dcs:tr:components", "")
		Meta("dcs:ui", "Template Management Dashboard")

		HTTP(func() {
			GET("/template/audit")
			Response(StatusOK)
		})

		Result(ArrayOf(String))
	})
})

// Contract Workflow Engine Service  (/contract/...)
var _contract_workflow_engine = Service("contract_workflow_engine", func() {
	Description("Contract Workflow Engine APIs (/contract/...)")

	Method("create", func() {
		Description("initiate new contract draft from template.")
		Meta("dcs:requirements", "DCS-IR-CWE-01", "DCS-IR-CWE-02")
		Meta("dcs:roles", "Contract Creator", "Sys. Contract Creator")
		Meta("dcs:cwe:components", "Contract Assembling")
		Meta("dcs:ui", "Contract Creation")

		HTTP(func() {
			POST("/contract/create")
			Response(StatusOK)
		})

		Result(String)
	})

	Method("submit", func() {
		Description("finalize and submit contract for negotiation/review. finalize and submit negotiated version. finalize review outcome. finalize decision. finalize review outcome.")
		Meta("dcs:requirements", "DCS-IR-CWE-01", "DCS-IR-CWE-03", "DCS-IR-CWE-06", "DCS-IR-CWE-09")
		Meta("dcs:roles", "Contract Creator", "Sys. Contract Creator", "Contract Negotiator", "Contract Reviewer", "Sys. Contract Reviewer", "Contract Approver", "Sys. Contract Approver")
		Meta("dcs:cwe:components", "")
		Meta("dcs:downstream:sm:component", "Signer Authorization & PoA application")
		Meta("dcs:ui", "Contract Creation", "Contract Negotiation", "Contract Review", "Contract Approval")

		HTTP(func() {
			POST("/contract/submit")
			Response(StatusOK)
		})

		Result(String)
	})

	Method("negotiate", func() {
		Description("propose changes.")
		Meta("dcs:requirements", "DCS-IR-CWE-03")
		Meta("dcs:roles", "Contract Negotiator")
		Meta("dcs:cwe:components", "Contract Assembling", "Contract Versioning")
		Meta("dcs:ui", "Contract Negotiation")

		HTTP(func() {
			POST("/contract/negotiate")
			Response(StatusOK)
		})

		Result(String)
	})

	Method("respond", func() {
		Description("provide feedback/findings. respond to counterpart changes.")
		Meta("dcs:requirements", "DCS-IR-CWE-03", "DCS-IR-CWE-05", "DCS-IR-CWE-06")
		Meta("dcs:roles", "Contract Negotiator", "Contract Reviewer", "Sys. Contract Reviewer")
		Meta("dcs:cwe:components", "Contract Versioning")
		Meta("dcs:ui", "Contract Negotiation", "Contract Review")

		HTTP(func() {
			POST("/contract/respond")
			Response(StatusOK)
		})

		Result(String)
	})

	Method("review", func() {
		Description("retrieve latest draft for comparison.")
		Meta("dcs:requirements", "DCS-IR-CWE-04")
		Meta("dcs:roles", "Contract Negotiator")
		Meta("dcs:cwe:components", "Contract Versioning")
		Meta("dcs:ui", "Contract Negotiation", "Contract Review")

		HTTP(func() {
			GET("/contract/review")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("retrieve", func() {
		Description("fetch submitted contract. fetch reviewed contract. fetch contract(s).")
		Meta("dcs:requirements", "DCS-IR-CWE-05", "DCS-IR-CWE-08", "DCS-IR-CWE-11", "DCS-IR-CWE-13")
		Meta("dcs:roles", "Contract Negotiator", "Contract Reviewer", "Sys. Contract Reviewer", "Contract Approver", "Sys. Contract Approver", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:cwe:components", "")
		Meta("dcs:downstream:sm:component", "Signer Authorization & PoA application")
		Meta("dcs:ui", "Contract Negotiation", "Contract Review", "Contract Approval", "Contract Management Dashboard")

		HTTP(func() {
			GET("/contract/retrieve")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("search", func() {
		Description("locate contracts by metadata or state. filter/search across lifecycle states.")
		Meta("dcs:requirements", "DCS-IR-CWE-07", "DCS-IR-CWE-11")
		Meta("dcs:roles", "Contract Reviewer", "Sys. Contract Reviewer", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:cwe:components", "")
		Meta("dcs:ui", "Contract Review", "Contract Management Dashboard")

		HTTP(func() {
			GET("/contract/search")
			Response(StatusOK)
		})

		Result(ArrayOf(Any))
	})

	Method("approve", func() {
		Description("approve and forward contract.")
		Meta("dcs:requirements", "DCS-IR-CWE-09", "DCS-IR-CWE-10")
		Meta("dcs:roles", "Contract Approver", "Sys. Contract Approver")
		Meta("dcs:cwe:components", "Contract Deployment for Service Provisioning")
		Meta("dcs:downstream:sm:component", "Signer Authorization & PoA application")
		Meta("dcs:ui", "Contract Approval")

		HTTP(func() {
			POST("/contract/approve")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("reject", func() {
		Description("reject with explanation.")
		Meta("dcs:requirements", "DCS-IR-CWE-09")
		Meta("dcs:roles", "Contract Approver", "Sys. Contract Approver")
		Meta("dcs:cwe:components", "")
		Meta("dcs:downstream:sm:component", "Signer Authorization & PoA application")
		Meta("dcs:ui", "Contract Approval")

		HTTP(func() {
			POST("/contract/reject")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("store", func() {
		Description("store evidence.")
		Meta("dcs:requirements", "DCS-IR-CWE-12")
		Meta("dcs:roles", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:cwe:components", "Contract Performance Tracking")
		Meta("dcs:ui", "Contract Management Dashboard")

		HTTP(func() {
			POST("/contract/store")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("terminate", func() {
		Description("terminate a contract.")
		Meta("dcs:requirements", "DCS-IR-CWE-12")
		Meta("dcs:roles", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:cwe:components", "")
		Meta("dcs:ui", "Contract Management Dashboard")

		HTTP(func() {
			POST("/contract/terminate")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("audit", func() {
		Description("generate audit record.")
		Meta("dcs:requirements", "DCS-IR-CWE-12", "DCS-IR-CWE-13")
		Meta("dcs:roles", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:cwe:components", "")
		Meta("dcs:ui", "Contract Management Dashboard")

		HTTP(func() {
			POST("/contract/audit")
			Response(StatusOK)
		})

		Result(ArrayOf(String))
	})
})

// Signature Management Service  (/signature/...)
var _signature_management = Service("signature_management", func() {
	Description("Signature Management APIs (/signature/...)")

	Method("retrieve", func() {
		Description("fetch contract & envelope.")
		Meta("dcs:requirements", "DCS-IR-SM-01")
		Meta("dcs:roles", "Contract Signer", "Sys. Contract Signer")
		Meta("dcs:ui", "Secure Contract Viewer")
		Meta("dcs:sm:components", "Signer Authorization & PoA application")

		HTTP(func() {
			GET("/signature/retrieve")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("verify", func() {
		Description("check contract integrity & envelope.")
		Meta("dcs:requirements", "DCS-IR-SM-02")
		Meta("dcs:roles", "Contract Signer", "Sys. Contract Signer")
		Meta("dcs:ui", "Secure Contract Viewer")
		Meta("dcs:sm:components", "Counterparty Authorization & PoA verification")

		HTTP(func() {
			POST("/signature/verify")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("apply", func() {
		Description("apply digital signature.")
		Meta("dcs:requirements", "DCS-IR-SM-03")
		Meta("dcs:roles", "Contract Signer", "Sys. Contract Signer")
		Meta("dcs:ui", "Secure Contract Viewer")
		Meta("dcs:sm:components", "Timestamping")

		HTTP(func() {
			POST("/signature/apply")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("validate", func() {
		Description("validate applied signature. validate contract signature(s).")
		Meta("dcs:requirements", "DCS-IR-SM-04", "DCS-IR-SM-05")
		Meta("dcs:roles", "Contract Signer", "Sys. Contract Signer", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:ui", "Secure Contract Viewer", "Signature Compliance Viewer")
		Meta("dcs:sm:components", "Counterparty Contract Signature Verification")

		HTTP(func() {
			POST("/signature/validate")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("revoke", func() {
		Description("revoke a signature.")
		Meta("dcs:requirements", "DCS-IR-SM-06")
		Meta("dcs:roles", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:ui", "Signature Compliance Viewer")
		Meta("dcs:sm:components", "Timestamping")

		HTTP(func() {
			POST("/signature/revoke")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("audit", func() {
		Description("retrieve compliance/audit logs.")
		Meta("dcs:requirements", "DCS-IR-SM-08")
		Meta("dcs:roles", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:ui", "Signature Compliance Viewer")
		Meta("dcs:sm:components", "")

		HTTP(func() {
			GET("/signature/audit")
			Response(StatusOK)
		})

		Result(ArrayOf(String))
	})

	Method("compliance", func() {
		Description("run compliance check.")
		Meta("dcs:requirements", "DCS-IR-SM-07")
		Meta("dcs:roles", "Contract Manager", "Sys. Contract Manager")
		Meta("dcs:ui", "Signature Compliance Viewer")
		Meta("dcs:sm:components", "")

		HTTP(func() {
			POST("/signature/compliance")
			Response(StatusOK)
		})

		Result(Any)
	})
})

// Contract Storage & Archive Service  (/archive/...)
var _contract_storage_archive = Service("contract_storage_archive", func() {
	Description("Contract Storage & Archive APIs (/archive/...)")

	Method("retrieve", func() {
		Description("retrieve archived items.")
		Meta("dcs:requirements", "DCS-IR-CSA-01", "DCS-IR-CSA-05")
		Meta("dcs:roles", "Archive Manager", "Contract Observer")
		Meta("dcs:ui", "Archive Manager Dashboard", "Archive Access")
		Meta("dcs:csa:components", "Signed Contract Archive")

		HTTP(func() {
			GET("/archive/retrieve")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("search", func() {
		Description("search archived records. search records by criteria.")
		Meta("dcs:requirements", "DCS-IR-CSA-01", "DCS-IR-CSA-05")
		Meta("dcs:roles", "Archive Manager", "Contract Observer")
		Meta("dcs:ui", "Archive Manager Dashboard", "Archive Access")
		Meta("dcs:csa:components", "Signed Contract Archive")
		HTTP(func() {
			GET("/archive/search")
			Response(StatusOK)
		})

		Result(ArrayOf(Any))
	})

	Method("store", func() {
		Description("store new contract or evidence.")
		Meta("dcs:requirements", "DCS-IR-CSA-02", "DCS-IR-CSA-06")
		Meta("dcs:roles", "Archive Manager")
		Meta("dcs:ui", "Archive Manager Dashboard")
		Meta("dcs:csa:components", "Signed Contract Archive")

		HTTP(func() {
			POST("/archive/store")
			Response(StatusOK)
		})

		Result(String)
	})
	Method("terminate", func() {
		Description("terminate contract/archive entry.")
		Meta("dcs:requirements", "DCS-IR-CSA-03", "DCS-IR-CSA-06")
		Meta("dcs:roles", "Archive Manager")
		Meta("dcs:ui", "Archive Manager Dashboard")
		Meta("dcs:csa:components", "Automated Alerts")

		HTTP(func() {
			POST("/archive/terminate")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("delete", func() {
		Description("permanently delete entry.")
		Meta("dcs:requirements", "DCS-IR-CSA-03", "DCS-IR-CSA-06")
		Meta("dcs:roles", "Archive Manager")
		Meta("dcs:ui", "Archive Manager Dashboard")
		Meta("dcs:csa:components", "Signed Contract Archive", "Automated Alerts")

		HTTP(func() {
			DELETE("/archive/delete")
			Response(StatusOK)
		})

		Result(Int)
	})

	Method("audit", func() {
		Description("retrieve audit logs.")
		Meta("dcs:requirements", "DCS-IR-CSA-04")
		Meta("dcs:roles", "Archive Manager")
		Meta("dcs:ui", "Archive Manager Dashboard")
		Meta("dcs:csa:components", "")

		HTTP(func() {
			GET("/archive/audit")
			Response(StatusOK)
		})

		Result(ArrayOf(String))
	})

})

// Process Audit & Compliance Management Service  (/pac/...)
var _pac = Service("pac", func() {
	Description("Process Audit & Compliance Management APIs (/pac/...)")

	Method("audit", func() {
		Description("trigger an audit on selected scope.")
		Meta("dcs:requirements", "DCS-IR-PACM-01")
		Meta("dcs:roles", "Auditor")
		Meta("dcs:ui", "Auditing Tool")
		Meta("dcs:pacm:components", "")

		HTTP(func() {
			POST("/pac/audit")
			Response(StatusOK)
		})

		Result(String)
	})

	Method("audit_report", func() {
		Description("generate and retrieve audit reports.")
		Meta("dcs:requirements", "DCS-IR-PACM-02")
		Meta("dcs:roles", "Auditor")
		Meta("dcs:ui", "Auditing Tool")
		Meta("dcs:pacm:components", "")

		HTTP(func() {
			GET("/pac/report")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("monitor", func() {
		Description("continuous monitoring and event retrieval.")
		Meta("dcs:requirements", "DCS-IR-PACM-03")
		Meta("dcs:roles", "Compliance Officer")
		Meta("dcs:ui", "Non-Compliance Investigation")
		Meta("dcs:pacm:components", "")

		HTTP(func() {
			GET("/pac/monitor")
			Response(StatusOK)
		})

		Result(Any)
	})

	Method("incident_report", func() {
		Description("submit non-compliance findings as case records.")
		Meta("dcs:requirements", "DCS-IR-PACM-04")
		Meta("dcs:roles", "Compliance Officer")
		Meta("dcs:ui", "Non-Compliance Investigation")
		Meta("dcs:pacm:components", "")

		HTTP(func() {
			POST("/pac/report")
			Response(StatusOK)
		})

		Result(Any)
	})
})

// Template Catalogue Integration Service (TR <-> XFSC Catalogue)
var _template_catalogue_integration = Service("template_catalogue_integration", func() {
	Description("Integration APIs between Template Repository (TR) and XFSC Catalogue for template discovery, request, and registration.")

	// TBD: callback path and method not defined in SRS
	Method("discover", func() {
		Description("Discover templates via XFSC Catalogue.")
		Meta("dcs:requirements", "DCS-IR-SI-01")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-01 does not specify concrete path).
			GET("/catalogue/template/discover")
			Response(StatusOK)
		})

		Result(Any)
	})

	// TBD: callback path and method not defined in SRS
	Method("request", func() {
		Description("Request template via XFSC Catalogue.")
		Meta("dcs:requirements", "DCS-IR-SI-01")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-01 does not specify concrete path).
			POST("/catalogue/template/request")
			Response(StatusOK)
		})

		Result(Any)
	})

	// TBD: callback path and method not defined in SRS
	Method("register", func() {
		Description("Register template into XFSC Catalogue.")
		Meta("dcs:requirements", "DCS-IR-SI-01")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-01 does not specify concrete path).
			POST("/catalogue/template/register")
			Response(StatusOK)
		})

		Result(Any)
	})
})

// External Orchestration Webhook Service (e.g. Node-RED)
var _orchestration_webhooks = Service("orchestration_webhooks", func() {
	Description("Webhook and callback endpoints for external orchestration tools (e.g. Node-RED).")

	// TBD: callback path and method not defined in SRS
	Method("node_red_webhook", func() {
		Description("Expose Node-Red - compatible endpoints and webhook callbacks.")
		Meta("dcs:requirements", "DCS-IR-SI-02")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-02 does not specify concrete path).
			POST("/webhook/node-red")
			Response(StatusOK)
		})

		Result(Any)
	})
})

// External Target System API Integration Service (DCS <-> External Systems)
var _external_target_system_api = Service("external_target_system_api", func() {
	Description("Integration APIs between DCS (CWE/SM/CSA) and external target systems (e.g., ERP or AI services): create/deploy actions, status queries, and event callbacks.")

	// TBD: path and method are not defined in SRS
	Method("action", func() {
		Description("Invoke external target system action (create/deploy) from DCS.")
		Meta("dcs:requirements", "DCS-IR-SI-05")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-05 does not specify concrete path).
			POST("/external/action")
			Response(StatusOK)
		})

		Result(Any)
	})

	// TBD: path and method are not defined in SRS
	Method("status", func() {
		Description("Query external target system status from DCS.")
		Meta("dcs:requirements", "DCS-IR-SI-05")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-05 does not specify concrete path).
			GET("/external/status")
			Response(StatusOK)
		})

		Result(Any)
	})

	// TBD: path and method are not defined in SRS
	Method("callback", func() {
		Description("Receive external target system callbacks/events into DCS.")
		Meta("dcs:requirements", "DCS-IR-SI-05")

		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-05 does not specify concrete path).
			POST("/external/callback")
			Response(StatusOK)
		})

		Result(Any)
	})

})

// DCS-to-DCS Information Service (counterparty integration)
var _dcs_to_dcs = Service("dcs_to_dcs", func() {
	Description("DCS supports direct interoperability between two or more DCS instances, enabling automated contract lifecycle operations across organizational boundaries.")

	// TBD: path and method are not defined in SRS
	Method("retrieve", func() {
		Description("Offer a policy-gated, read-only contract information endpoint between a DCS instance and a counterparty DCS")

		Meta("dcs:requirements", "DCS-IR-SI-06")
		HTTP(func() {
			// NOTE: Defined placeholder path (DCS-IR-SI-06 does not specify concrete path).
			GET("/peer/retrieve")
			Response(StatusOK)
		})

		Result(Any)
	})
})

/**
 *	TBD:
 * 	 - Software Interfaces (e.g. DCS-IR-SI-09)
 * 	 - UC-09-02 – System Configuration & User Management: Handles role-based access, security, and
system configurations.
*/
