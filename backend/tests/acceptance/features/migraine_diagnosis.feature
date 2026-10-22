Feature: Assessment API contracts with synthetic model responses
  These scenarios exercise the source application using local storage and stubbed Bedrock.
  They do not establish clinical accuracy, latency SLA, or cloud deployment.

  Scenario: Generated assessment can be retrieved by its owner
    Given a configured local assessment application
    When an authenticated owner submits a valid synthetic case
    Then the assessment is stored and retrievable by that owner
    And a different owner cannot retrieve that case

  Scenario: Empty symptoms are rejected before model invocation
    Given a configured local assessment application
    When an authenticated owner submits a case without symptoms
    Then the API rejects the request with status 400

  Scenario: Provider failure is returned honestly
    Given a configured local assessment application
    When Bedrock fails while assessing a synthetic case
    Then the API rejects the request with status 503
    And no case response has been persisted
