from __future__ import annotations

import json
import os

import gradio as gr

from raven_biocomputer import BioComputer

computer = BioComputer(workspace_root=os.getenv("RAVEN_BIOCOMPUTER_RUNS", "runs"))
TOOLS = {item["name"]: item for item in computer.registry.list()}


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


with gr.Blocks(title="Raven BioComputer") as demo:
    gr.Markdown(
        """
# 🧬 Raven BioComputer
### Give biology agents a private, auditable workstation

This CPU-friendly demo runs deterministic dry-lab tools inside isolated run folders and emits
Raven Evidence Graph, JSpace Chain, Home for AI, Hermes Edge, and OpenClinical bridge records.
It does **not** provide clinical advice or autonomous wet-lab execution.
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
    gr.Markdown(
        "Built for the Raven AI ecosystem. Local-first core, tool-first routing, evidence-linked outputs."
    )

if __name__ == "__main__":
    demo.launch()
