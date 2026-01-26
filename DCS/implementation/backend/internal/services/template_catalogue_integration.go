package services

import (
	"context"
	templatecatalogueintegration "digital-contracting-service/gen/template_catalogue_integration"

	"goa.design/clue/log"
)

// TemplateCatalogueIntegration service example implementation.
// The example methods log the requests and return zero values.
type templateCatalogueIntegrationsrvc struct{}

// NewTemplateCatalogueIntegration returns the TemplateCatalogueIntegration
// service implementation.
func NewTemplateCatalogueIntegration() templatecatalogueintegration.Service {
	return &templateCatalogueIntegrationsrvc{}
}

// Discover templates via XFSC Catalogue.
func (s *templateCatalogueIntegrationsrvc) Discover(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "templateCatalogueIntegration.discover")
	return
}

// Request template via XFSC Catalogue.
func (s *templateCatalogueIntegrationsrvc) Request(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "templateCatalogueIntegration.request")
	return
}

// Register template into XFSC Catalogue.
func (s *templateCatalogueIntegrationsrvc) Register(ctx context.Context) (res any, err error) {
	log.Printf(ctx, "templateCatalogueIntegration.register")
	return
}
