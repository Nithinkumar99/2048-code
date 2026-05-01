# ──────────────────────────────────────────────────────────
#  2048 Web Edition — Docker Image
#
#  Build : docker build -t 2048-web .
#  Run   : docker run -p 5000:5000 2048-web
#  Open  : http://localhost:5000
# ──────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install/pkgs --no-cache-dir -r requirements.txt


# ── Stage 2: lean runtime image ────────────────────────────
FROM python:3.12-slim

LABEL maintainer="Nithin Kumar" \
      description="2048 — Flask web game" \
      version="2.0"

# Copy installed packages from builder
COPY --from=builder /install/pkgs /usr/local

# Non-root user
RUN useradd -m -s /bin/sh appuser

WORKDIR /app

COPY app.py requirements.txt ./
# Support both flat layout (index.html alongside Dockerfile)
# and nested layout (templates/index.html)
RUN mkdir -p templates
COPY index.html ./templates/

RUN chown -R appuser:appuser /app

USER appuser

# Flask/gunicorn port
EXPOSE 5000

# Health-check — Docker will mark container unhealthy if Flask stops
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Gunicorn: 2 workers, bind to all interfaces
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "app:app"]