package design

import (
	. "goa.design/goa/v3/dsl"
)

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
