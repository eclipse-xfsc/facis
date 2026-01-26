package services

import (
	"context"
	externaltargetsystemapi "digital-contracting-service/gen/external_target_system_api"

	"goa.design/clue/log"
)

// ExternalTargetSystemApi service example implementation.
// The example methods log the requests and return zero values.
type externalTargetSystemAPIsrvc struct{}

// NewExternalTargetSystemAPI returns the ExternalTargetSystemApi service
// implementation.
func NewExternalTargetSystemAPI() externaltargetsystemapi.Service {
	return &externalTargetSystemAPIsrvc{}
}

// Invoke external target system action (create/deploy) from DCS.
func (s *externalTargetSystemAPIsrvc) Action(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "externalTargetSystemAPI.action")
	return
}

// Query external target system status from DCS.
func (s *externalTargetSystemAPIsrvc) Status(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "externalTargetSystemAPI.status")
	return
}

// Receive external target system callbacks/events into DCS.
func (s *externalTargetSystemAPIsrvc) Callback(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "externalTargetSystemAPI.callback")
	return
}
