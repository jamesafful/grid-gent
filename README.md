
# Grid-Gent Demo

Minimal, self-contained demo of an **agentic AI-style assistant for a city's distribution grid**.

This version is intentionally simple and uses **only the Python standard library** so you can
run it anywhere (including GitHub Codespaces) with just:

```bash
python main.py
```

It does **not** connect to a real grid, SCADA, or LLM API. Instead it uses:

- A tiny *multi-agent* pattern (IntentAgent, PlanningAgent, NarratorAgent)
- Deterministic **tools** (simple power-flow-style stub and feeder metadata)
- A lightweight HTTP server for a browser-based UI

The architecture mirrors what a real Grid-Gent could look like, but everything is safe and
demo-only.

## Structure

```text
grid-gent/
  main.py                 # HTTP server + API + web UI entrypoint
  gridgent/
    __init__.py
    tools.py              # Deterministic "grid tools" (fake power flow, feeder metadata)
    agents.py             # IntentAgent, PlanningAgent, NarratorAgent
    orchestrator.py       # GridGentOrchestrator (ties agents + tools together)
  templates/
    index.html            # Single-page UI for the demo
```

## Running

1. Make sure you're in the project root (where `main.py` lives).
2. Run:

   ```bash
   python main.py
   ```

   By default it serves on port `8000`. You can override it with:

   ```bash
   GRID_GENT_PORT=8080 python main.py
   ```

3. In your browser (or Codespaces forwarded port), open:

   ```
   http://localhost:8000
   ```

4. Type a scenario, e.g.:

   - `What happens on feeder F2 if we add 5 MW of rooftop PV?`
   - `Simulate adding 3 MW of load on feeder F1.`

   Click **Run Grid-Gent** and you will see:
   - A narrative answer
   - A breakdown of steps and agent/tool activity

## API

- `POST /api/ask`

  Request body:

  ```json
  { "query": "What happens on feeder F2 if we add 5 MW of rooftop PV?" }
  ```

  Response body:

  ```jsonc
  {
    "task_id": "uuid-...",
    "answer": "Long human-readable explanation...",
    "steps": [
      { "role": "intent_agent", "content": "...", "meta": { "...": "..." } },
      { "role": "planning_agent", "content": "...", "meta": { "...": "..." } },
      { "role": "tool", "content": "Ran simplified power-flow scenario.", "meta": { "...": "..." } },
      { "role": "tool", "content": "Retrieved static feeder metadata.", "meta": { "...": "..." } },
      { "role": "narrator_agent", "content": "Generated human-readable explanation for operator/planner.", "meta": {} }
    ]
  }
  ```

## Extending

To move from this demo to a more realistic Grid-Gent:

- Swap `gridgent.tools` stubs with calls into actual grid simulators and data sources.
- Replace the rule-based logic in `agents.py` with actual LLM calls (keeping the same high-level structure).
- Add guardrails and approvals so suggestions remain advisory and reviewed by engineers.
