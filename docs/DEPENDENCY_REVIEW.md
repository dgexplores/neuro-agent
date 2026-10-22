# Dependency review — 22 October 2026

The runtime was upgraded to FastAPI 0.160.0, Starlette 1.9.0, Pydantic 2.14.1,
PyJWT 2.15.1 and updated multipart, AWS SDK and environment packages. Unused
python-jose/ecdsa, passlib, scientific-computing and image-processing packages
were removed from the active installation boundary. The backend does not import
them. `requirements-runtime.in` records intent; `requirements-lambda.txt` pins
the complete resolved cross-platform runtime. `requirements.txt` includes that
lock plus test tools. Recompile deliberately with `uv pip compile` and repeat
verification when updating dependencies.

The complete pinned runtime audit reports **zero known vulnerabilities**. The
full frontend npm audit also reports **zero vulnerabilities**. These are dated
advisory snapshots, not proof against unknown vulnerabilities. CI repeats both
audits. A fresh Python environment passed all 115 backend tests, the frontend
passed 14 tests, and the freshly rebuilt Linux x86_64 Python 3.11 Lambda layer
passed an actual Linux import and HTTP health check. CDK assertions and the
runtime container health/OpenAPI/authentication smoke checks passed.

FastAPI now returns 401 (with a bearer challenge) for missing authentication;
the endpoint tests were updated to that HTTP authentication contract. Invalid
or expired credentials remain rejected. No authentication bypass was added.

Live Bedrock calls and public AWS deployment have not been exercised. Archived
upstream examples/vendor directories are historical material, not dependencies
installed by the current application. Credentials in inherited Git history are
removed in the publication copy; local original clones are retained separately.
