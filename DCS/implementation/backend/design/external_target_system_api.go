package design

import (
	. "goa.design/goa/v3/dsl"
)

// External Target System API Integration Service (DCS <-> External Systems)
var _ = Service("ExternalTargetSystemApi", func() {
	Description("Integration APIs between DCS (CWE/SM/CSA) and external target systems (e.g., ERP or AI service): create/deploy actions, status queries, and event callbacks.")

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
