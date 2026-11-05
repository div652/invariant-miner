# Model endpoints

| File | Use | Endpoint |
|---|---|---|
| `luna-cao.json` | **Standard for every benchmark** | GPT-5.6 Luna on CAO directly (`127.0.0.1:4141/v1`, Responses API), as the AHE campaign 34 agent: reasoning summaries on, encrypted reasoning returned and sent back each turn, effort medium (Luna's provider default; c34 sends no effort, DSH's pi-ai must name one to request summaries), 128K output cap, no temperature. |
| `luna-proxy-high.json` | Record of the JobBench parity run (2026-11-05) | GPT-5.6 Luna through agentic-evolution's model_serve proxy on :8018 (CAO upstream), reasoning high, 262K context, 32K output: the reference JobBench overlay's settings. |

Why the standard needs a named effort: DSH's pi-ai adapter sends `reasoning: {effort, summary: "auto"}` and
`include: ["reasoning.encrypted_content"]` only when an effort is configured. Without one it sends no `reasoning`
field and Luna returns empty summaries (the campaign 23 behaviour); `effort: "none"` would turn reasoning off.
