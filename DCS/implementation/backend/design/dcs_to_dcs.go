package design

import (
	. "goa.design/goa/v3/dsl"
)

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
