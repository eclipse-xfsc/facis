[← System Features](05_system_features.md) | [↑ Table of Contents](../README.md)

---

## 6 Appendix

### Example of an Attested TLS Protocol

An example of an attested TLS protocol as specified in Section 5.2 is the attested TLS protocol implemented at [github.com/Fraunhofer-AISEC/cmc](github.com/Fraunhofer-AISEC/cmc) as an Apache 2.0-licensed project. Below is an example of how to implement a simplistic reverse proxy with the protocol. Note that this example would not fit the requirements for an ingress gateway laid out in this specification. Instructions on how to deploy the REQUIRED CMC daemon can be found in the linked repository.

```go
package main

import (
	"crypto/tls"
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"

	atls "github.com/Fraunhofer-AISEC/cmc/attestedtls"
)

type Endpoint struct {
	Prefix    string
	ForwardTo *url.URL
}

// Obtaining the TLS certificate is out of scope for this example
func GetTlsConfig() *tls.Config

func ReverseProxy(endpoints []Endpoint, addr, cmcAddress string, policy string) error {
	// There are no special requirements for the TLS certificates for the attestation protocol
	tlsConf := GetTlsConfig().Clone()

	// We require at least TLS version 1.3
	tlsConf.MinVersion = tls.VersionTLS13

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		key := r.Host + r.URL.Path

		var destination *url.URL
		for _, endpoint := range endpoints {
			if strings.HasPrefix(key, endpoint.Prefix) {
				destination = endpoint.ForwardTo
			}
		}

		if destination == nil {
			w.WriteHeader(http.StatusNotFound)
		}

		httputil.NewSingleHostReverseProxy(destination).ServeHTTP(w, r)
	})

	listener, err := atls.Listen("tcp", addr, tlsConf,
		// The address the cmc is listening on
		atls.WithCmcAddr(cmcAddress),
		// Specify that we require mutual TLS
		atls.WithMtls(true),
		// Set the attestation type to mutual attestation.
		atls.WithAttest(atls.Attest_Mutual),
		// Include a custom javascript policy to evaluate the attestation.
		atls.WithCmcPolicies([]byte(policy)),
	)
	if err != nil {
		return fmt.Errorf("failed to listen for incoming connections")
	}

	server := &http.Server{
		Addr:    addr,
		Handler: handler,
	}

	return server.Serve(listener)
}
```

---

[← System Features](05_system_features.md) | [↑ Table of Contents](../README.md)

