package design

import (
	. "goa.design/goa/v3/dsl"
)

// Contract Storage & Archive Service  (/archive/...)
var _ = Service("ContractStorageArchive", func() {
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
