#syntax=docker/dockerfile:1.4

FROM ubuntu:noble as builder

RUN <<EOT
set -ex
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
set -ex
cd /_lock
uv sync \
    --locked \
    --no-dev \
    --no-install-project
EOT

COPY . /src
RUN --mount=type=cache,target=/root/.cache <<EOT
set -ex
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
set -ex
groupadd -r tesseract
useradd --system --home /app --gid tesseract --no-user-group tesseract
EOT

ENTRYPOINT ["tini", "-v", "--", "/docker-entrypoint.sh"]

# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT

# Update OS packages, then clear APT cache and lists
RUN <<EOT
set -ex
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    ca-certificates \
    tini \
    python3.12 \
    libpython3.12 \
    libpcre3 \
    libxml2 \
    curl

apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Copy runtime files
COPY --chmod=755 docker-entrypoint.sh /
COPY --from=builder --chown=tesseract:tesseract /app /app
COPY --chown=tesseract:tesseract ./app.py /app/app.py
COPY --chown=tesseract:tesseract ./etc /app/etc

# Replace runtime user and cwd
USER tesseract
WORKDIR /app

# Tests to ensure correct configuration and permissions
RUN <<EOT
set -ex
# Print python version
python -V
# Print sys.path, https://docs.python.org/3/library/site.html#command-line-interface
python -Im site
# Ensure folders have correct permissions
python -Ic 'import os; assert os.access("/docker-entrypoint.sh", os.X_OK)'
python -Ic 'import os; assert os.access("/app", os.W_OK)'
python -Ic 'import os; assert os.access("/app/lib", os.R_OK)'
python -Ic 'import os; assert os.access("/app/etc", os.R_OK)'
python -Ic 'import project'
# Print dependency folder size
echo "The dependency folder is $(du -sh /app/lib | awk '{print $1}')"
EOT
