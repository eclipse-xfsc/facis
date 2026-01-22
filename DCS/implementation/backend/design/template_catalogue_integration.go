package design

import (
	. "goa.design/goa/v3/dsl"
)

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
