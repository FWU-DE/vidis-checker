FROM ghcr.io/astral-sh/uv:0.5.31-python3.12-bookworm AS builder

WORKDIR /app

COPY uv.lock pyproject.toml /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ------------------------------------------------------------------+
# 1) download the Playwright browsers once, inside the builder stage
# ------------------------------------------------------------------+
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
# `uv sync` created the virtual-env in .venv, so the CLI is available:
RUN /app/.venv/bin/playwright install --with-deps chromium

FROM python:3.12-slim AS runtime

# ---------------------------------------------------------------+
# 2) system deps all three browsers need on Debian/Ubuntu slim
# ---------------------------------------------------------------+
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates libasound2 libatk-bridge2.0-0 libatk1.0-0 \
        libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 \
        libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
        libxshmfence1 libxkbcommon0 libxss1 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
# 3) copy the browsers that were downloaded earlier
COPY --from=builder /ms-playwright /ms-playwright

ENV PATH="/app/.venv/bin:$PATH"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    XDG_CACHE_HOME=/app/.cache

COPY app.py /app/
COPY generate_report.py /app/
COPY run_classification.py /app/
COPY run_agent.py /app/
COPY src /app/src

RUN addgroup --system app && \
    adduser  --system --group --home /app app && \
    chown -R app:app /app
ENV HOME=/app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]