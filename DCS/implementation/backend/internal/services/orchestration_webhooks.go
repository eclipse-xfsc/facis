package services

import (
	"context"
	orchestrationwebhooks "digital-contracting-service/gen/orchestration_webhooks"

	"goa.design/clue/log"
)

// OrchestrationWebhooks service example implementation.
// The example methods log the requests and return zero values.
type orchestrationWebhookssrvc struct{}

// NewOrchestrationWebhooks returns the OrchestrationWebhooks service
// implementation.
func NewOrchestrationWebhooks() orchestrationwebhooks.Service {
	return &orchestrationWebhookssrvc{}
}

// Expose Node-Red - compatible endpoints and webhook callbacks.
func (s *orchestrationWebhookssrvc) NodeRedWebhook(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "orchestrationWebhooks.node_red_webhook")
	return
}
