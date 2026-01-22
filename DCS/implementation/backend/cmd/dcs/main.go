package main

import (
	"context"
	contractstoragearchive "digital-contracting-service/gen/contract_storage_archive"
	dcstodcs "digital-contracting-service/gen/dcs_to_dcs"
	externaltargetsystemapi "digital-contracting-service/gen/external_target_system_api"
	orchestrationwebhooks "digital-contracting-service/gen/orchestration_webhooks"
	pac "digital-contracting-service/gen/pac"
	signaturemanagement "digital-contracting-service/gen/signature_management"
	templatecatalogueintegration "digital-contracting-service/gen/template_catalogue_integration"
	templaterepository "digital-contracting-service/gen/template_repository"
	"digital-contracting-service/internal/service"
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
		contractStorageArchiveSvc       contractstoragearchive.Service
		dcsToDcsSvc                     dcstodcs.Service
		externalTargetSystemAPISvc      externaltargetsystemapi.Service
		orchestrationWebhooksSvc        orchestrationwebhooks.Service
		pacSvc                          pac.Service
		signatureManagementSvc          signaturemanagement.Service
		templateCatalogueIntegrationSvc templatecatalogueintegration.Service
		templateRepositorySvc           templaterepository.Service
	)
	{
		contractStorageArchiveSvc = service.NewContractStorageArchive()
		dcsToDcsSvc = service.NewDcsToDcs()
		externalTargetSystemAPISvc = service.NewExternalTargetSystemAPI()
		orchestrationWebhooksSvc = service.NewOrchestrationWebhooks()
		pacSvc = service.NewPac()
		signatureManagementSvc = service.NewSignatureManagement()
		templateCatalogueIntegrationSvc = service.NewTemplateCatalogueIntegration()
		templateRepositorySvc = service.NewTemplateRepository()
	}

	// Wrap the services in endpoints that can be invoked from other services
	// potentially running in different processes.
	var (
		contractStorageArchiveEndpoints       *contractstoragearchive.Endpoints
		dcsToDcsEndpoints                     *dcstodcs.Endpoints
		externalTargetSystemAPIEndpoints      *externaltargetsystemapi.Endpoints
		orchestrationWebhooksEndpoints        *orchestrationwebhooks.Endpoints
		pacEndpoints                          *pac.Endpoints
		signatureManagementEndpoints          *signaturemanagement.Endpoints
		templateCatalogueIntegrationEndpoints *templatecatalogueintegration.Endpoints
		templateRepositoryEndpoints           *templaterepository.Endpoints
	)
	{
		contractStorageArchiveEndpoints = contractstoragearchive.NewEndpoints(contractStorageArchiveSvc)
		contractStorageArchiveEndpoints.Use(debug.LogPayloads())
		contractStorageArchiveEndpoints.Use(log.Endpoint)
		dcsToDcsEndpoints = dcstodcs.NewEndpoints(dcsToDcsSvc)
		dcsToDcsEndpoints.Use(debug.LogPayloads())
		dcsToDcsEndpoints.Use(log.Endpoint)
		externalTargetSystemAPIEndpoints = externaltargetsystemapi.NewEndpoints(externalTargetSystemAPISvc)
		externalTargetSystemAPIEndpoints.Use(debug.LogPayloads())
		externalTargetSystemAPIEndpoints.Use(log.Endpoint)
		orchestrationWebhooksEndpoints = orchestrationwebhooks.NewEndpoints(orchestrationWebhooksSvc)
		orchestrationWebhooksEndpoints.Use(debug.LogPayloads())
		orchestrationWebhooksEndpoints.Use(log.Endpoint)
		pacEndpoints = pac.NewEndpoints(pacSvc)
		pacEndpoints.Use(debug.LogPayloads())
		pacEndpoints.Use(log.Endpoint)
		signatureManagementEndpoints = signaturemanagement.NewEndpoints(signatureManagementSvc)
		signatureManagementEndpoints.Use(debug.LogPayloads())
		signatureManagementEndpoints.Use(log.Endpoint)
		templateCatalogueIntegrationEndpoints = templatecatalogueintegration.NewEndpoints(templateCatalogueIntegrationSvc)
		templateCatalogueIntegrationEndpoints.Use(debug.LogPayloads())
		templateCatalogueIntegrationEndpoints.Use(log.Endpoint)
		templateRepositoryEndpoints = templaterepository.NewEndpoints(templateRepositorySvc)
		templateRepositoryEndpoints.Use(debug.LogPayloads())
		templateRepositoryEndpoints.Use(log.Endpoint)
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
			handleHTTPServer(ctx, u, contractStorageArchiveEndpoints, dcsToDcsEndpoints, externalTargetSystemAPIEndpoints, orchestrationWebhooksEndpoints, pacEndpoints, signatureManagementEndpoints, templateCatalogueIntegrationEndpoints, templateRepositoryEndpoints, &wg, errc, *dbgF)
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
