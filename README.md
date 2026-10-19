# Enterprise MCP + LangGraph Agent (Starter Project)

A runnable learning project that demonstrates:

- Two MCP servers: employee lookup and internal-document search
- A LangGraph agent that discovers and calls MCP tools
- Basic tool-level authorization and input validation
- Human approval for a sensitive action (simulated employee record update)
- Structured logging, timeouts, and tests


## Architecture

```text
User -> LangGraph agent / LLM
          | discovers tools through MCP clients
          +--> Employee MCP server (stdio) --> data/employees.json
          +--> Document MCP server (stdio) --> data/knowledge_base.json
          |
          +--> application policy: allowlist, input validation, approval gate

Logs: application JSON logs to stderr (keep stdout clean for stdio MCP)
```

## Requirements

- Python 3.11+
- An API key for a chat model supported by LangChain (example uses OpenAI)

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env`, then set your model key. Do not commit `.env`.

```bash
cp .env.example .env
```

### 4. Run the agent

```bash
python -m agent.main
```

Try prompts such as:

- `Find employee 101.`
- `Search the knowledge base for leave policy.`
- `What is the engineering on-call process?`

The MCP servers are launched by the agent as subprocesses using stdio. Run the agent from the project root so the relative paths resolve correctly.

## Run tests

```bash
pytest -q
```

Tests cover input validation and document search without needing an LLM API key.

## Project layout

```text
mcp-enterprise-agent/
  agent/
    main.py              # LangGraph + MCP clients
    policy.py            # tool allowlist and approval gate example
  mcp_servers/
    employee_server.py   # employee tools
    documents_server.py  # document search tool
  data/
    employees.json       # synthetic employee records
    knowledge_base.json  # synthetic internal docs
  tests/
  .env.example
  requirements.txt
```

## Security notes

1. **Authentication:** stdio is a local process transport and does not itself authenticate a remote user. Add user identity at the host/application layer. For remote Streamable HTTP deployments, implement the MCP authorization specification and validate token issuer, audience, expiry, and scopes.
2. **Authorization:** the sample denies access to sensitive fields and demonstrates a confirmation gate for updates. Replace the demo policy with server-side, per-user authorization. Never rely on the LLM to enforce permissions.
3. **Prompt injection:** documents are untrusted data. The agent should treat retrieved text as data, not instructions. Tool outputs can still influence model behavior; enforce controls outside the model.
4. **Secrets:** use a secret manager in production. Never place API keys in source code or log them.
5. **Logging:** do not log raw prompts, credentials, or sensitive employee information. This sample logs tool names and outcomes only.
6. **Side effects:** the sample update tool is deliberately not exposed to the agent by default. If enabling it, require authenticated approval and idempotency controls.
7. **Network:** restrict outbound destinations for tools that call external APIs and defend against SSRF.

## Troubleshooting

- `ModuleNotFoundError`: activate the virtual environment and reinstall `requirements.txt`.
- MCP server startup errors: run `python mcp_servers/employee_server.py` to inspect stderr; use the same interpreter as the agent.
- Model authentication errors: verify `OPENAI_API_KEY` in `.env` and that your account has API access.
- Stdio protocol errors: never print debug output to stdout from an MCP server. Use stderr or logging.

## Production hardening checklist

- [ ] OIDC/OAuth authentication and authorization
- [ ] Per-tool permission matrix and tenant isolation
- [ ] Schema validation and bounded query limits
- [ ] Approval workflow for writes / irreversible actions
- [ ] OpenTelemetry traces, metrics, and dashboards
- [ ] Rate limits, deadlines, retries only for safe operations
- [ ] Dependency pinning, vulnerability scanning, and server allowlisting
- [ ] Automated prompt-injection and data-exfiltration tests
- [ ] Persistent audit trail with access controls
- [ ] Deployment health checks and operational runbooks
