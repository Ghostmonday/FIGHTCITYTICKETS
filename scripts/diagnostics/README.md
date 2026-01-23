# Diagnostics Toolkit

This folder contains network and container diagnostics used to debug local
connectivity issues (e.g., `ERR_CONNECTION_RESET` in the browser).

## When to use

- Browser can open `http://127.0.0.1:3000` or `http://localhost` but requests
  reset or hang.
- Nginx is running, but proxy requests time out.
- Docker containers are healthy but host connectivity is broken.

## Tools

### `debug_connection.py`

Runs a full set of checks and writes NDJSON logs to:

`/home/evan/Documents/Projects/FightSFTickets/.cursor/debug.log`

Checks include:
- TCP connect to ports 80 and 3000.
- HTTP requests to host ports 80 and 3000.
- Nginx → web container request.
- Web container local request.
- Container IPs and host → container IP request.
- Web container listening sockets and env vars.
- Nginx logs and UFW status.

Run:

```bash
sudo python3 /home/evan/Documents/Projects/FightSFTickets/scripts/diagnostics/debug_connection.py
```

### `test_connection.sh`

Quick smoke test for port listeners and nginx ↔ web connectivity.
Writes the same log file above, and also POSTs to the local debug ingest endpoint.

Run:

```bash
sudo bash /home/evan/Documents/Projects/FightSFTickets/scripts/diagnostics/test_connection.sh
```

## Notes for AI operators

- Clear the log before each run using the delete-file tool (not shell `rm`).
- Do not log secrets or API keys.
- Leave instrumentation in place until a post-fix verification run succeeds.
