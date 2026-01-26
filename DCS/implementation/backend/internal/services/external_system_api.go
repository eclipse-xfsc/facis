package services

import (
	"context"
	externalsystemapi "digital-contracting-service/gen/external_system_api"

	"goa.design/clue/log"
)

// ExternalSystemApi service example implementation.
// The example methods log the requests and return zero values.
type externalSystemAPIsrvc struct{}

// NewExternalSystemAPI returns the ExternalSystemApi service implementation.
func NewExternalSystemAPI() externalsystemapi.Service {
	return &externalSystemAPIsrvc{}
}

// Invoke external target system action (create/deploy) from DCS.
func (s *externalSystemAPIsrvc) Action(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "externalSystemAPI.action")
	return
}

// Query external target system status from DCS.
func (s *externalSystemAPIsrvc) Status(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "externalSystemAPI.status")
	return
}

// Receive external target system callbacks/events into DCS.
func (s *externalSystemAPIsrvc) Callback(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "externalSystemAPI.callback")
	return
}
