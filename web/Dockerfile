# syntax=docker/dockerfile:1

# ---------- stage 1: validate GLB payloads before anything ships ----------
FROM node:22-alpine AS validate
WORKDIR /chk
COPY tools/check-glb.js ./check-glb.mjs
COPY models ./models
RUN node check-glb.mjs \
      models/architecture.glb models/garden.glb models/interior.glb \
      models/critter_koi.glb models/critter_frog.glb models/critter_dragonfly.glb \
      models/critter_cat.glb models/critter_sparrow.glb

# ---------- stage 2: static runtime ----------
FROM nginx:1.27-alpine AS runtime

COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY web/index.html /usr/share/nginx/html/
COPY web/src /usr/share/nginx/html/src
COPY web/vendor /usr/share/nginx/html/vendor
COPY web/models /usr/share/nginx/html/models

# nginx:alpine ships a wget; assert the entry document is served
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

EXPOSE 80
