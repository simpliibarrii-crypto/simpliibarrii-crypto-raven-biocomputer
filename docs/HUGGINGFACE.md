# Hugging Face deployment

Create a Gradio Space named `bclermo/raven-biocomputer`, then upload the repository contents or connect the Space to the GitHub repository.

The Space entry point is `app.py`. It requires CPU Basic only for the included deterministic tools.

Recommended Space settings:

- SDK: Gradio
- App file: `app.py`
- Visibility: Public for synthetic demo data, Private for governed data
- Persistent storage: optional; run receipts otherwise reset when the Space restarts
- Secrets: none required for the core demo

Do not upload PHI, credentials, proprietary datasets, or wet-lab control secrets to a public Space.
