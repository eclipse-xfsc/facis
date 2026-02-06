package design

import (
	. "goa.design/goa/v3/dsl"
)

// Template Repository Service  (/template/...)
var _ = Service("TemplateRepository", func() {
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
