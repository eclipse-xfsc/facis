package design

import (
	. "goa.design/goa/v3/dsl"
)

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
