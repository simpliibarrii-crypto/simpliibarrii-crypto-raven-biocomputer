from __future__ import annotations

import json
import os

import gradio as gr

from raven_biocomputer import BioComputer

computer = BioComputer(workspace_root=os.getenv("RAVEN_BIOCOMPUTER_RUNS", "runs"))
TOOLS = {item["name"]: item for item in computer.registry.list()}

BRAND_CSS = """
:root {
  --obsidian: #050505;
  --carbon: #0d0d0f;
  --graphite: #151518;
  --crimson: #c8273f;
  --crimson-bright: #f04460;
  --champagne: #c9ad7d;
  --champagne-light: #e7d3af;
  --ivory: #f4efe7;
  --ash: #8f8a83;
}
.gradio-container {
  color-scheme: dark !important;
  max-width: 1180px !important;
  margin: 0 auto !important;
  padding: 28px !important;
  background:
    radial-gradient(circle at 88% 0%, rgba(200,39,63,.18), transparent 30rem),
    radial-gradient(circle at 3% 35%, rgba(201,173,125,.06), transparent 26rem),
    #050505 !important;
  color: var(--ivory) !important;
  font-family: "Avenir Next", Inter, system-ui, sans-serif !important;
}
body { background: #050505 !important; }
.bio-hero {
  position: relative;
  overflow: hidden;
  margin-bottom: 18px;
  padding: clamp(24px, 5vw, 48px);
  border: 1px solid rgba(201,173,125,.18);
  border-radius: 22px;
  background: linear-gradient(145deg, rgba(21,21,24,.96), rgba(7,7,8,.98));
  box-shadow: 0 28px 80px rgba(0,0,0,.48), 0 0 38px rgba(200,39,63,.07);
}
.bio-hero::after {
  content: "";
  position: absolute;
  right: -55px;
  top: -65px;
  width: 270px;
  height: 270px;
  border: 1px solid rgba(201,173,125,.16);
  border-radius: 50%;
  box-shadow: inset 0 0 0 46px rgba(200,39,63,.025);
}
.bio-kicker {
  color: var(--crimson-bright);
  font: 700 .72rem/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
  letter-spacing: .18em;
}
.bio-hero h1 {
  margin: 12px 0 9px;
  color: var(--ivory);
  font-family: Georgia, "Iowan Old Style", serif;
  font-size: clamp(2.2rem, 6vw, 4.8rem);
  font-weight: 600;
  line-height: .98;
  letter-spacing: -.05em;
}
.bio-hero h1 span { color: var(--champagne); }
.bio-hero p { max-width: 820px; margin: 0; color: #b8b0a5; font-size: 1.02rem; }
.bio-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px; }
.bio-meta span {
  padding: 7px 10px;
  border: 1px solid rgba(201,173,125,.17);
  border-radius: 999px;
  background: rgba(5,5,5,.56);
  color: var(--ash);
  font: .68rem ui-monospace, SFMono-Regular, Menlo, monospace;
}
.gradio-container .block,
.gradio-container .form,
.gradio-container .panel {
  border-color: rgba(201,173,125,.16) !important;
  border-radius: 15px !important;
  background: rgba(21,21,24,.9) !important;
  box-shadow: none !important;
}
.gradio-container label,
.gradio-container .label-wrap { color: var(--champagne-light) !important; }
.gradio-container input,
.gradio-container textarea {
  border-color: rgba(201,173,125,.16) !important;
  background: #080809 !important;
  color: var(--ivory) !important;
}
.gradio-container input:focus,
.gradio-container textarea:focus {
  border-color: var(--champagne) !important;
  box-shadow: 0 0 0 3px rgba(201,173,125,.09) !important;
}
.gradio-container button.primary {
  border: 1px solid var(--crimson-bright) !important;
  background: linear-gradient(180deg, var(--crimson-bright), var(--crimson)) !important;
  color: #fff8f5 !important;
  font-weight: 700 !important;
}
.gradio-container button.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 28px rgba(200,39,63,.2) !important;
}
.bio-footer {
  margin-top: 18px;
  padding: 15px 18px;
  border-left: 3px solid var(--crimson);
  background: rgba(200,39,63,.045);
  color: var(--ash);
  font-size: .9rem;
}
.bio-footer strong { color: var(--champagne-light); }
@media (max-width: 640px) {
  .gradio-container { padding: 12px !important; }
  .bio-hero { padding: 25px 19px; }
}
"""


def example_for(tool: str) -> str:
    return json.dumps(TOOLS[tool]["input_example"], indent=2)


def run_tool(task: str, tool: str, payload_text: str):
    try:
        payload = json.loads(payload_text)
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a JSON object.")
        receipt = computer.execute(task=task, tool=tool, payload=payload)
        summary = (
            f"Status: {receipt['status']}\n"
            f"Run: {receipt['run_id']}\n"
            f"Policy: {receipt['policy']['level']}\n"
            f"Reason: {receipt['policy']['reason']}"
        )
        return summary, receipt
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}", {}


with gr.Blocks(title="Raven BioComputer", css=BRAND_CSS) as demo:
    gr.HTML(
        """
        <section class="bio-hero">
          <div class="bio-kicker">RAVEN ECOSYSTEM / BOUNDED BIOLOGY COMPUTE</div>
          <h1>Raven <span>BioComputer</span></h1>
          <p>A private workstation for biology agents. Run deterministic dry-lab tools inside isolated workspaces and receive policy-aware, evidence-linked artifact receipts.</p>
          <div class="bio-meta">
            <span>ALPHA RESEARCH SOFTWARE</span>
            <span>LOCAL-FIRST CORE</span>
            <span>NO AUTONOMOUS WET-LAB EXECUTION</span>
          </div>
        </section>
        """
    )
    with gr.Row():
        task = gr.Textbox(
            label="Research task",
            value="Calculate basic properties for this demonstration sequence.",
        )
        tool = gr.Dropdown(
            choices=list(TOOLS),
            value="sequence_stats",
            label="Bounded biology tool",
        )
    payload = gr.Code(
        label="JSON payload",
        language="json",
        value=example_for("sequence_stats"),
    )
    tool.change(example_for, inputs=tool, outputs=payload)
    run = gr.Button("Run inside BioComputer", variant="primary")
    status = gr.Textbox(label="Run status")
    receipt = gr.JSON(label="Auditable run receipt")
    run.click(run_tool, inputs=[task, tool, payload], outputs=[status, receipt])
    gr.HTML(
        """
        <div class="bio-footer"><strong>Bounded by design.</strong> The demo provides deterministic computational tools and receipts. It does not provide clinical advice, pathogen engineering, autonomous wet-lab actions, or policy bypasses.</div>
        """
    )


if __name__ == "__main__":
    demo.launch()
