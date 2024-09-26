FROM ubuntu:mantic as builder

# To use python3.10, switch to ubuntu:jammy

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates \
    python3-setuptools \
    python3.12-dev
EOT

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app

COPY pyproject.toml /_lock/
COPY uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache <<EOT
cd /_lock
uv sync \
    --frozen \
    --no-dev \
    --no-install-project
EOT

COPY . /src
RUN --mount=type=cache,target=/root/.cache <<EOT
uv pip install \
    --python=$UV_PROJECT_ENVIRONMENT \
    --no-deps \
    /src
EOT

# ============================================================================ #

FROM ubuntu:mantic as runtime

# Include virtual environment in PATH
ENV PATH=/app/bin:$PATH

# Create the runtime user and group
RUN <<EOT
groupadd -r tesseract
useradd --system --home /app --gid tesseract --no-user-group tesseract
EOT

ENTRYPOINT ["tini", "-v", "--", "/docker-entrypoint.sh"]

# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT

# Update OS packages, then clear APT cache and lists
RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    ca-certificates \
    tini \
    python3.12 \
    libpython3.12 \
    libpcre3 \
    libxml2

apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Copy runtime files
COPY docker-entrypoint.sh /
COPY etc /app/etc

COPY --from=builder --chown=tesseract:tesseract /app /app
COPY --chown=tesseract:tesseract ./app.py /app/app.py

# Replace runtime user and cwd
USER tesseract
WORKDIR /app

# Tests to ensure correct configuration and permissions
RUN <<EOT
python -V
python -Im site
python -Ic 'import server'
ls -l /docker-entrypoint.sh
ls -la /app
ls -l /app/etc
EOT
