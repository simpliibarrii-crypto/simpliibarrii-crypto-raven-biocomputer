FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAVEN_BIOCOMPUTER_RUNS=/workspace/runs

RUN useradd --create-home --uid 10001 raven
WORKDIR /workspace

COPY pyproject.toml README.md LICENSE ./
COPY raven_biocomputer ./raven_biocomputer
COPY app.py ./app.py
RUN pip install --no-cache-dir ".[api,space,mcp]"

RUN mkdir -p /workspace/runs && chown -R raven:raven /workspace
USER raven

EXPOSE 7860 8042
CMD ["python", "app.py"]
