package main

import (
	"context"
	contractstoragearchive "digital-contracting-service/gen/contract_storage_archive"
	contractworkflowengine "digital-contracting-service/gen/contract_workflow_engine"
	dcstodcs "digital-contracting-service/gen/dcs_to_dcs"
	externaltargetsystemapi "digital-contracting-service/gen/external_target_system_api"
	orchestrationwebhooks "digital-contracting-service/gen/orchestration_webhooks"
	pac "digital-contracting-service/gen/pac"
	signaturemanagement "digital-contracting-service/gen/signature_management"
	templatecatalogueintegration "digital-contracting-service/gen/template_catalogue_integration"
	templaterepository "digital-contracting-service/gen/template_repository"
	"digital-contracting-service/internal/controller"
	"flag"
	"fmt"
	"net"
	"net/url"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"goa.design/clue/debug"
	"goa.design/clue/log"
)

func main() {
	// Define command line flags, add any other flag required to configure the
	// service.
	var (
		hostF     = flag.String("host", "local", "Server host (valid values: local)")
		domainF   = flag.String("domain", "", "Host domain name (overrides host domain specified in service design)")
		httpPortF = flag.String("http-port", "", "HTTP port (overrides host HTTP port specified in service design)")
		secureF   = flag.Bool("secure", false, "Use secure scheme (https or grpcs)")
		dbgF      = flag.Bool("debug", false, "Log request and response bodies")
	)
	flag.Parse()

	// Setup logger. Replace logger with your own log package of choice.
	format := log.FormatJSON
	if log.IsTerminal() {
		format = log.FormatTerminal
	}
	ctx := log.Context(context.Background(), log.WithFormat(format))
	if *dbgF {
		ctx = log.Context(ctx, log.WithDebug())
		log.Debugf(ctx, "debug logs enabled")
	}
	log.Print(ctx, log.KV{K: "http-port", V: *httpPortF})

	// Initialize the services.
	var (
		templateRepositorySvc           templaterepository.Service
		contractWorkflowEngineSvc       contractworkflowengine.Service
		signatureManagementSvc          signaturemanagement.Service
		contractStorageArchiveSvc       contractstoragearchive.Service
		pacSvc                          pac.Service
		templateCatalogueIntegrationSvc templatecatalogueintegration.Service
		orchestrationWebhooksSvc        orchestrationwebhooks.Service
		externalTargetSystemAPISvc      externaltargetsystemapi.Service
		dcsToDcsSvc                     dcstodcs.Service
	)
	{
		templateRepositorySvc = controller.NewTemplateRepository()
		contractWorkflowEngineSvc = controller.NewContractWorkflowEngine()
		signatureManagementSvc = controller.NewSignatureManagement()
		contractStorageArchiveSvc = controller.NewContractStorageArchive()
		pacSvc = controller.NewPac()
		templateCatalogueIntegrationSvc = controller.NewTemplateCatalogueIntegration()
		orchestrationWebhooksSvc = controller.NewOrchestrationWebhooks()
		externalTargetSystemAPISvc = controller.NewExternalTargetSystemAPI()
		dcsToDcsSvc = controller.NewDcsToDcs()
	}

	// Wrap the services in endpoints that can be invoked from other services
	// potentially running in different processes.
	var (
		templateRepositoryEndpoints           *templaterepository.Endpoints
		contractWorkflowEngineEndpoints       *contractworkflowengine.Endpoints
		signatureManagementEndpoints          *signaturemanagement.Endpoints
		contractStorageArchiveEndpoints       *contractstoragearchive.Endpoints
		pacEndpoints                          *pac.Endpoints
		templateCatalogueIntegrationEndpoints *templatecatalogueintegration.Endpoints
		orchestrationWebhooksEndpoints        *orchestrationwebhooks.Endpoints
		externalTargetSystemAPIEndpoints      *externaltargetsystemapi.Endpoints
		dcsToDcsEndpoints                     *dcstodcs.Endpoints
	)
	{
		templateRepositoryEndpoints = templaterepository.NewEndpoints(templateRepositorySvc)
		templateRepositoryEndpoints.Use(debug.LogPayloads())
		templateRepositoryEndpoints.Use(log.Endpoint)
		contractWorkflowEngineEndpoints = contractworkflowengine.NewEndpoints(contractWorkflowEngineSvc)
		contractWorkflowEngineEndpoints.Use(debug.LogPayloads())
		contractWorkflowEngineEndpoints.Use(log.Endpoint)
		signatureManagementEndpoints = signaturemanagement.NewEndpoints(signatureManagementSvc)
		signatureManagementEndpoints.Use(debug.LogPayloads())
		signatureManagementEndpoints.Use(log.Endpoint)
		contractStorageArchiveEndpoints = contractstoragearchive.NewEndpoints(contractStorageArchiveSvc)
		contractStorageArchiveEndpoints.Use(debug.LogPayloads())
		contractStorageArchiveEndpoints.Use(log.Endpoint)
		pacEndpoints = pac.NewEndpoints(pacSvc)
		pacEndpoints.Use(debug.LogPayloads())
		pacEndpoints.Use(log.Endpoint)
		templateCatalogueIntegrationEndpoints = templatecatalogueintegration.NewEndpoints(templateCatalogueIntegrationSvc)
		templateCatalogueIntegrationEndpoints.Use(debug.LogPayloads())
		templateCatalogueIntegrationEndpoints.Use(log.Endpoint)
		orchestrationWebhooksEndpoints = orchestrationwebhooks.NewEndpoints(orchestrationWebhooksSvc)
		orchestrationWebhooksEndpoints.Use(debug.LogPayloads())
		orchestrationWebhooksEndpoints.Use(log.Endpoint)
		externalTargetSystemAPIEndpoints = externaltargetsystemapi.NewEndpoints(externalTargetSystemAPISvc)
		externalTargetSystemAPIEndpoints.Use(debug.LogPayloads())
		externalTargetSystemAPIEndpoints.Use(log.Endpoint)
		dcsToDcsEndpoints = dcstodcs.NewEndpoints(dcsToDcsSvc)
		dcsToDcsEndpoints.Use(debug.LogPayloads())
		dcsToDcsEndpoints.Use(log.Endpoint)
	}

	// Create channel used by both the signal handler and server goroutines
	// to notify the main goroutine when to stop the server.
	errc := make(chan error)

	// Setup interrupt handler. This optional step configures the process so
	// that SIGINT and SIGTERM signals cause the services to stop gracefully.
	go func() {
		c := make(chan os.Signal, 1)
		signal.Notify(c, syscall.SIGINT, syscall.SIGTERM)
		errc <- fmt.Errorf("%s", <-c)
	}()

	var wg sync.WaitGroup
	ctx, cancel := context.WithCancel(ctx)

	// Start the servers and send errors (if any) to the error channel.
	switch *hostF {
	case "local":
		{
			addr := "http://0.0.0.0:8991"
			u, err := url.Parse(addr)
			if err != nil {
				log.Fatalf(ctx, err, "invalid URL %#v\n", addr)
			}
			if *secureF {
				u.Scheme = "https"
			}
			if *domainF != "" {
				u.Host = *domainF
			}
			if *httpPortF != "" {
				h, _, err := net.SplitHostPort(u.Host)
				if err != nil {
					log.Fatalf(ctx, err, "invalid URL %#v\n", u.Host)
				}
				u.Host = net.JoinHostPort(h, *httpPortF)
			} else if u.Port() == "" {
				u.Host = net.JoinHostPort(u.Host, "80")
			}
			handleHTTPServer(ctx, u, templateRepositoryEndpoints, contractWorkflowEngineEndpoints, signatureManagementEndpoints, contractStorageArchiveEndpoints, pacEndpoints, templateCatalogueIntegrationEndpoints, orchestrationWebhooksEndpoints, externalTargetSystemAPIEndpoints, dcsToDcsEndpoints, &wg, errc, *dbgF)
		}

	default:
		log.Fatal(ctx, fmt.Errorf("invalid host argument: %q (valid hosts: local)", *hostF))
	}

	// Wait for signal.
	log.Printf(ctx, "exiting (%v)", <-errc)

	// Send cancellation signal to the goroutines.
	cancel()

	wg.Wait()
	log.Printf(ctx, "exited")
}
