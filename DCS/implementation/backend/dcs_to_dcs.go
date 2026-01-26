package dcs

import (
	"context"
	dcstodcs "digital-contracting-service/gen/dcs_to_dcs"

	"goa.design/clue/log"
)

// DcsToDcs service example implementation.
// The example methods log the requests and return zero values.
type dcsToDcssrvc struct{}

// NewDcsToDcs returns the DcsToDcs service implementation.
func NewDcsToDcs() dcstodcs.Service {
	return &dcsToDcssrvc{}
}

// Offer a policy-gated, read-only contract information endpoint between a DCS
// instance and a counterparty DCS
func (s *dcsToDcssrvc) Retrieve(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "dcsToDcs.retrieve")
	return
}
