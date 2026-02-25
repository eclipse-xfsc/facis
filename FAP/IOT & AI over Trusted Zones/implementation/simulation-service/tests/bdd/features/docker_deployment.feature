Feature: Docker Deployment
  As a DevOps engineer
  I want containerized deployment
  So that I can deploy consistently across environments

  Scenario: Container startup
    Given the Docker image is built
    When I run the container with default configuration
    Then all simulation services should start within 30 seconds
    And health check endpoint should return 200 OK

  Scenario: Configuration via environment variables
    Given environment variable SIMULATION_SEED=54321
    And environment variable TIME_ACCELERATION=10
    When I start the container
    Then simulation should use the specified seed
    And time should be accelerated 10x

  Scenario: Volume mounting for data persistence
    Given a volume mounted at /data
    When simulation generates data
    Then data should be persisted to the volume
    And data should survive container restart

  Scenario: Docker Compose multi-service deployment
    Given a docker-compose.yml with simulation and MQTT broker
    When I run docker-compose up
    Then all services should start and interconnect
    And simulation should publish to the MQTT broker
