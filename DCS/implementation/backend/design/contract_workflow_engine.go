package design

import (
	. "goa.design/goa/v3/dsl"
)

// Contract Workflow Engine Service  (/contract/...)
var _ = Service("ContractWorkflowEngine", func() {
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
