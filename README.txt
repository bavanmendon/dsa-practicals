Version: v1.0
Type: Codebase
Message: 
First commit.
Basic CRUD functionality.

Version: v2.0
Type: Codebase
Message:
Added a new part to implement containerized grpc server and a local grpc client communicating with each other.
Added reflection and interceptors on the server end.
Added a .proto file for protocol buffers and compiled.
Added a script to test grpc vs rest performance.

Version: v3.0
Type: Codebase
Message:
Modified gRPC service with MongoDB integration.
Modified REST service with retry & circuit breaker.
Added docker-compose.yml with all three services (REST, gRPC, MongoDB)
Modified .proto file for a success/failure indication.

Version: v3.1
Type: Feature
Message:
Added the CRUD operations: Update and delete.

Version: v4.0
Type: Codebase
Message:
Modified REST service for scraping by Prometheus and tracing by OpenTelemetry.
Modified gRPC service for scraping by Prometheus.
Added prometheus.yml for Prometheus configuration.
Added datasource.yml for Golden Signals on Grafana.
Added dashboard.yml for Grafana configuration.
Added golden-signals.json for panel configuration.
Added otel-collector-config.yml for OpenTelemtry configuration.
Modified docker-compose.yml to additionally include grafana, otel, jaeger and prometheus services.
Modified requirements.txt files for both gRPC server and REST service to include necessary libraries.

Version: v5.0
Type: Codebase
Message:
Modified REST and gRPC service to include mTLS handshake.
Modified REST service to check for Keycloack generated JWT and a new '/healthz' route.
Added traefik.yml for HTTP/HTTPS traffic routing.
Added dynamic.yml for TLS certificate configuration.
Added certificates for REST and gRPC services.
Added root certificate with certificate signature requests.
Ignored private keys for root, REST and gRPC certificates.
Modified docker-compose.yml to additionally include traefik and keycloak.
Modified requirement.txt files for both gRPC and REST service to include necessary libraries.

Version: v5.1
Type: Report
Message:
Added reports for all 5 tasks.

Version: v5.2
Type: Report
Message:
Edited report 5.
