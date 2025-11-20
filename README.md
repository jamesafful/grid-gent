# Grid-Gent Demo (v4) – Uploadable Grid Models

Agentic-style assistant for city distribution grid scenarios with:

- Unknown/smalltalk handling (no fake scenarios for 'hi', 'why', etc.).
- Conceptual explanation mode when no feeder/MW is given.
- Scenario mode (simulation / hosting_capacity) for actual what-if questions.
- **New:** Upload your own grid model (JSON or CSV) and the demo will use it.

## Running

```bash
python main.py
```

Then open http://localhost:8000.

On the right side of the UI you can upload a `.json` or `.csv` file with feeder definitions.
The server will replace the built-in demo feeders with your uploaded ones (still using a simplified
calculation, not a full AC power flow).
