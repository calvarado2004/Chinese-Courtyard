# syntax=docker/dockerfile:1
# Regenerates every GLB with headless Blender. Run via:
#   docker compose --profile pipeline run --rm pipeline
ARG BLENDER_VERSION=4.2.3

FROM python:3.11-slim AS blender-installer
ARG BLENDER_VERSION
RUN apt-get update \
 && apt-get install -y --no-install-recommends xz-utils ca-certificates curl \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL -o /tmp/blender.tar.xz \
      "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
 && tar -xJf /tmp/blender.tar.xz -C /opt \
 && mv "/opt/blender-${BLENDER_VERSION}-linux-x64" /opt/blender \
 && rm /tmp/blender.tar.xz

FROM python:3.11-slim AS pipeline
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libxkbcommon0 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=blender-installer /opt/blender /opt/blender
ENV PATH="/opt/blender:${PATH}" \
    BLENDER_USER_SCRIPTS=/opt/blender-user
WORKDIR /work
COPY blender ./blender
CMD ["blender", "-b", "-P", "blender/build.py", "--", "--stage", "5", "--no-render"]
