# Start from the NVIDIA CUDA base image
FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------
LABEL maintainer="Shehryar"
LABEL version="1.0"
LABEL description="Me in 60s"
# Provide CUDA-related labels for clarity (optional)
LABEL com.nvidia.cuda.version="12.3.2"
LABEL com.nvidia.cudnn.version="9"

# ---------------------------------------------------------------------------
# Environment Variables & Shell
# ---------------------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_PREFER_BINARY=1 \
    PYTHONUNBUFFERED=1 \
    HTTP_TIMEOUT=600

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ---------------------------------------------------------------------------
# System Dependencies
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      python3-dev \
      python3-pip \
      python3.10-venv \
      fonts-dejavu-core \
      rsync \
      git \
      jq \
      moreutils \
      aria2 \
      wget \
      curl \
      libglib2.0-0 \
      libsm6 \
      libgl1 \
      libxrender1 \
      libxext6 \
      ffmpeg \
      libgoogle-perftools-dev \
      procps && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Upgrade pip
# ---------------------------------------------------------------------------
RUN python3 -m pip install --upgrade pip

# ---------------------------------------------------------------------------
# Copy project requirements and install
# ---------------------------------------------------------------------------
COPY requirements.txt /tmp/requirements.txt
RUN pip install --use-pep517 --no-cache-dir -r /tmp/requirements.txt

# Add the rest of the application
COPY . .

CMD ["python3", "-u", "60_handler.py"]