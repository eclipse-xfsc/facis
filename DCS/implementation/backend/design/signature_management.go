package design

import (
	. "goa.design/goa/v3/dsl"
)

// Signature Management Service  (/signature/...)
var _ = Service("SignatureManagement", func() {
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
