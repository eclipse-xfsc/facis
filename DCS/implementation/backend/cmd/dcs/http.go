package main

import (
	"context"
	contractstoragearchive "digital-contracting-service/gen/contract_storage_archive"
	contractworkflowengine "digital-contracting-service/gen/contract_workflow_engine"
	dcstodcs "digital-contracting-service/gen/dcs_to_dcs"
	externaltargetsystemapi "digital-contracting-service/gen/external_target_system_api"
	contractstoragearchivesvr "digital-contracting-service/gen/http/contract_storage_archive/server"
	contractworkflowenginesvr "digital-contracting-service/gen/http/contract_workflow_engine/server"
	dcstodcssvr "digital-contracting-service/gen/http/dcs_to_dcs/server"
	externaltargetsystemapisvr "digital-contracting-service/gen/http/external_target_system_api/server"
	orchestrationwebhookssvr "digital-contracting-service/gen/http/orchestration_webhooks/server"
	processauditandcompliancesvr "digital-contracting-service/gen/http/process_audit_and_compliance/server"
	signaturemanagementsvr "digital-contracting-service/gen/http/signature_management/server"
	templatecatalogueintegrationsvr "digital-contracting-service/gen/http/template_catalogue_integration/server"
	templaterepositorysvr "digital-contracting-service/gen/http/template_repository/server"
	orchestrationwebhooks "digital-contracting-service/gen/orchestration_webhooks"
	processauditandcompliance "digital-contracting-service/gen/process_audit_and_compliance"
	signaturemanagement "digital-contracting-service/gen/signature_management"
	templatecatalogueintegration "digital-contracting-service/gen/template_catalogue_integration"
	templaterepository "digital-contracting-service/gen/template_repository"
	"net/http"
	"net/url"
	"sync"
	"time"

	"goa.design/clue/debug"
	"goa.design/clue/log"
	goahttp "goa.design/goa/v3/http"
)

// handleHTTPServer starts configures and starts a HTTP server on the given
// URL. It shuts down the server if any error is received in the error channel.
func handleHTTPServer(ctx context.Context, u *url.URL, contractStorageArchiveEndpoints *contractstoragearchive.Endpoints, contractWorkflowEngineEndpoints *contractworkflowengine.Endpoints, dcsToDcsEndpoints *dcstodcs.Endpoints, externalTargetSystemAPIEndpoints *externaltargetsystemapi.Endpoints, orchestrationWebhooksEndpoints *orchestrationwebhooks.Endpoints, processAuditAndComplianceEndpoints *processauditandcompliance.Endpoints, signatureManagementEndpoints *signaturemanagement.Endpoints, templateCatalogueIntegrationEndpoints *templatecatalogueintegration.Endpoints, templateRepositoryEndpoints *templaterepository.Endpoints, wg *sync.WaitGroup, errc chan error, dbg bool) {

	// Provide the transport specific request decoder and response encoder.
	// The goa http package has built-in support for JSON, XML and gob.
	// Other encodings can be used by providing the corresponding functions,
	// see goa.design/implement/encoding.
	var (
		dec = goahttp.RequestDecoder
		enc = goahttp.ResponseEncoder
	)

	// Build the service HTTP request multiplexer and mount debug and profiler
	// endpoints in debug mode.
	var mux goahttp.Muxer
	{
		mux = goahttp.NewMuxer()
		if dbg {
			// Mount pprof handlers for memory profiling under /debug/pprof.
			debug.MountPprofHandlers(debug.Adapt(mux))
			// Mount /debug endpoint to enable or disable debug logs at runtime.
			debug.MountDebugLogEnabler(debug.Adapt(mux))
		}
	}

	// Wrap the endpoints with the transport specific layers. The generated
	// server packages contains code generated from the design which maps
	// the service input and output data structures to HTTP requests and
	// responses.
	var (
		contractStorageArchiveServer       *contractstoragearchivesvr.Server
		contractWorkflowEngineServer       *contractworkflowenginesvr.Server
		dcsToDcsServer                     *dcstodcssvr.Server
		externalTargetSystemAPIServer      *externaltargetsystemapisvr.Server
		orchestrationWebhooksServer        *orchestrationwebhookssvr.Server
		processAuditAndComplianceServer    *processauditandcompliancesvr.Server
		signatureManagementServer          *signaturemanagementsvr.Server
		templateCatalogueIntegrationServer *templatecatalogueintegrationsvr.Server
		templateRepositoryServer           *templaterepositorysvr.Server
	)
	{
		eh := errorHandler(ctx)
		contractStorageArchiveServer = contractstoragearchivesvr.New(contractStorageArchiveEndpoints, mux, dec, enc, eh, nil)
		contractWorkflowEngineServer = contractworkflowenginesvr.New(contractWorkflowEngineEndpoints, mux, dec, enc, eh, nil)
		dcsToDcsServer = dcstodcssvr.New(dcsToDcsEndpoints, mux, dec, enc, eh, nil)
		externalTargetSystemAPIServer = externaltargetsystemapisvr.New(externalTargetSystemAPIEndpoints, mux, dec, enc, eh, nil)
		orchestrationWebhooksServer = orchestrationwebhookssvr.New(orchestrationWebhooksEndpoints, mux, dec, enc, eh, nil)
		processAuditAndComplianceServer = processauditandcompliancesvr.New(processAuditAndComplianceEndpoints, mux, dec, enc, eh, nil)
		signatureManagementServer = signaturemanagementsvr.New(signatureManagementEndpoints, mux, dec, enc, eh, nil)
		templateCatalogueIntegrationServer = templatecatalogueintegrationsvr.New(templateCatalogueIntegrationEndpoints, mux, dec, enc, eh, nil)
		templateRepositoryServer = templaterepositorysvr.New(templateRepositoryEndpoints, mux, dec, enc, eh, nil)
	}

	// Configure the mux.
	contractstoragearchivesvr.Mount(mux, contractStorageArchiveServer)
	contractworkflowenginesvr.Mount(mux, contractWorkflowEngineServer)
	dcstodcssvr.Mount(mux, dcsToDcsServer)
	externaltargetsystemapisvr.Mount(mux, externalTargetSystemAPIServer)
	orchestrationwebhookssvr.Mount(mux, orchestrationWebhooksServer)
	processauditandcompliancesvr.Mount(mux, processAuditAndComplianceServer)
	signaturemanagementsvr.Mount(mux, signatureManagementServer)
	templatecatalogueintegrationsvr.Mount(mux, templateCatalogueIntegrationServer)
	templaterepositorysvr.Mount(mux, templateRepositoryServer)

	var handler http.Handler = mux
	if dbg {
		// Log query and response bodies if debug logs are enabled.
		handler = debug.HTTP()(handler)
	}
	handler = log.HTTP(ctx)(handler)

	// Start HTTP server using default configuration, change the code to
	// configure the server as required by your service.
	srv := &http.Server{Addr: u.Host, Handler: handler, ReadHeaderTimeout: time.Second * 60}
	for _, m := range contractStorageArchiveServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range contractWorkflowEngineServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range dcsToDcsServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range externalTargetSystemAPIServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range orchestrationWebhooksServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range processAuditAndComplianceServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range signatureManagementServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range templateCatalogueIntegrationServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}
	for _, m := range templateRepositoryServer.Mounts {
		log.Printf(ctx, "HTTP %q mounted on %s %s", m.Method, m.Verb, m.Pattern)
	}

	(*wg).Add(1)
	go func() {
		defer (*wg).Done()

		// Start HTTP server in a separate goroutine.
		go func() {
			log.Printf(ctx, "HTTP server listening on %q", u.Host)
			errc <- srv.ListenAndServe()
		}()

		<-ctx.Done()
		log.Printf(ctx, "shutting down HTTP server at %q", u.Host)

		// Shutdown gracefully with a 30s timeout.
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		err := srv.Shutdown(ctx)
		if err != nil {
			log.Printf(ctx, "failed to shutdown: %v", err)
		}
	}()
}

// errorHandler returns a function that writes and logs the given error.
// The function also writes and logs the error unique ID so that it's possible
// to correlate.
func errorHandler(logCtx context.Context) func(context.Context, http.ResponseWriter, error) {
	return func(ctx context.Context, w http.ResponseWriter, err error) {
		log.Printf(logCtx, "ERROR: %s", err.Error())
	}
}
