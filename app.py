import json
import os

import gradio as gr

from raven_biocomputer import BioComputer

computer = BioComputer(os.getenv("RAVEN_BIOCOMPUTER_RUNS", "runs"))


def run_task(task: str, tool: str, payload: str):
    try:
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            raise ValueError("payload must decode to a JSON object")
        return computer.execute(task=task, tool=tool, payload=parsed)
    except Exception as exc:
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}


with gr.Blocks(title="Raven BioComputer") as demo:
    gr.Markdown(
        "# 🧬 Raven BioComputer\n"
        "A private, auditable biology workstation for AI agents."
    )
    task = gr.Textbox(
        value="Calculate properties for this demonstration sequence.",
        label="Task",
    )
    tool = gr.Dropdown(
        [item["name"] for item in computer.registry.list()],
        value="sequence_stats",
        label="Tool",
    )
    payload = gr.Code(
        value='{"sequence":"ACGTACGTNN"}',
        language="json",
        label="Payload",
    )
    output = gr.JSON(label="Raven run receipt")
    gr.Button("Run").click(run_task, [task, tool, payload], output)
    gr.Markdown(
        "Dry-lab demonstration only. No clinical advice or autonomous wet-lab control."
    )

if __name__ == "__main__":
    demo.launch()
