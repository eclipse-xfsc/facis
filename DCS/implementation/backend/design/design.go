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
