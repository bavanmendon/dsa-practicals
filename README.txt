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
