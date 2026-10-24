# Oracle cloud verification — 24 October 2026

Live application: **https://neuro-161-118-164-31.sslip.io/**

The initial release `7f4c4dd36f66a64dfb3d8601a98e0f55c694ef36` was installed
from a Git archive and a production frontend build on the existing Oracle
Always Free ARM host shared with Vigil. No new compute, disk, or paid cloud
service was provisioned. The configured Gemini project's billing was previously
verified disabled. Capacity and model quotas can still affect availability.

## Completed live checks

- Caddy obtained a valid public HTTPS certificate. Normal certificate checking
  passed; no insecure TLS option was used for verification.
- Backend health reported `gemini: not_checked`, distinguishing liveness from
  live model availability. Home, `/demo` and `/history` returned the React app;
  a nonexistent asset returned 404. Missing bearer authentication returned 401.
- One server-owned fictional headache example completed through the public API
  using the actual Gemini adapter and structured response parser, then saved to
  SQLite. The complete API/model/save/ownership check took approximately 15 seconds.
- Same-session retrieval returned the saved response. Another newly issued
  session received 404 for that case ID. An unauthenticated lookup returned 401.
- A repeated assessment attempt received 429. A demo token on the unrestricted
  medication endpoint received 403. These checks did not make additional model calls.
- A separate real browser session started without an account or API key, ran
  the fictional example, displayed its result and retrieved it on Saved cases
  after loading `/history` directly. Two model calls were used in total.
- Restarting only `neuro-backend-1` retained the API check's exact saved response
  and its consumed session quota. A repeated attempt still returned 429.
- The nonroot backend ran within its 512 MB memory cap; a post-check snapshot
  showed approximately 52 MiB in use. This is an observation, not a load benchmark.
- Vigil HTTPS readiness remained healthy while the shared edge was configured.

## Automated evidence and release status

The complete 181-test backend suite passed locally and in the offline Linux
container. All 25 frontend tests and the production build passed. Native ARM
image checks verified UID 10001, read-only root, writable SQLite volume and owner
isolation. Hosted frontend, dependency audit, container, AWS synthesis and ARM
packaging checks passed on the initial release candidates.

The original hosted backend job repeatedly stalled without finalized logs.
Its isolated test context initially omitted the new deployment module; that
collection error was corrected. The full suite then passed locally. A later
hosted runner still did not report a result, including after changing to direct
Python execution with explicit process and step deadlines. The workflow now
runs the unchanged full suite on an ARM runner matching Oracle. Check the
[current Actions results](https://github.com/dgexplores/neuro-agent/actions)
for hosted sign-off; a pending or cancelled job is not a pass.

The first live installation was manual, using the locally verified artifacts.
The [Oracle deployment workflow](../.github/workflows/oracle-deploy.yml) remains
gated on all automated jobs. It does not skip a failed or incomplete backend
check. A workflow definition or successful manual installation does not prove
that the hosted automated rollout completed.

## Scope and recovery

This is a single-host educational application using invented inputs. Model
confidence values are not calibrated medical accuracy, and the output must not
be used for diagnosis or treatment. The image/operator endpoints were tested
with offline provider contracts, not opened to public demo tokens.

Private runtime configuration and JWT secrets are outside Git. Cases and quotas
use the `neuro-cases` named volume. Deployment rollback retains that volume;
it does not undo database schema changes. Session expiry does not delete saved
fictional cases or SQLite quota records. Production identity, retention policy,
clinical validation and high availability are outside the current scope.

The preserved AWS infrastructure was synthesized and packaged but has not been
deployed or tested against live Bedrock in this adaptation.
