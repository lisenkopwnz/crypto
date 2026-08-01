FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock* ./

ENV VIRTUAL_ENV="/opt/venv"
RUN uv venv /opt/venv --clear && \
    uv pip install --no-cache-dir -e .

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]