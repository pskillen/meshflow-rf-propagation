# syntax=docker/dockerfile:1
# hadolint global ignore=DL3008,DL3009
ARG UPSTREAM_REF

FROM python:3.14-slim AS builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG UPSTREAM_REF
ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/root \
    TERM=xterm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libbz2-dev \
        gdal-bin \
        libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY docker/ docker/

RUN test -n "${UPSTREAM_REF}" \
    && git clone https://github.com/meshtastic/meshtastic-site-planner.git upstream

WORKDIR /build/upstream

RUN git checkout "${UPSTREAM_REF}" \
    && git submodule update --init --recursive

WORKDIR /build

RUN python3 docker/apply_upstream_patches.py /build/upstream

WORKDIR /build/upstream

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /build/upstream/splat
RUN chmod +x build configure install \
    && sed -i.bak "s/-march=\$cpu/-march=native/g" build \
    && printf "8\n4\n" | ./configure \
    && ./install splat

WORKDIR /build/upstream/splat/utils
RUN chmod +x build \
    && ./build all \
    && cp srtm2sdf /build/upstream \
    && cp srtm2sdf-hd /build/upstream

RUN cp -a . /build/upstream/splat

WORKDIR /build/upstream
RUN chmod +x /build/upstream/splat/splat \
    && chmod +x /build/upstream/splat/srtm2sdf \
    && chmod +x /build/upstream/splat/citydecoder \
    && chmod +x /build/upstream/splat/bearing \
    && chmod +x /build/upstream/splat/fontdata \
    && chmod +x /build/upstream/splat/usgs2sdf

ENV UPSTREAM_ROOT=/build/upstream \
    SPLAT_PREFIX=/build/upstream/splat \
    SDF_BAKE_OUT=/data/sdf

RUN mkdir -p /data/sdf \
    && python3 /build/docker/bake_uk_sdf.py

FROM python:3.14-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SDF_DIR=/data/sdf \
    REDIS_URL=redis://redis:6379/0 \
    MPLCONFIGDIR=/tmp/mpl \
    HOME=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gdal-bin \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser \
    && mkdir -p /tmp/mpl \
    && chown appuser:appuser /tmp/mpl

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder /build/upstream/app /app/app
COPY --from=builder /build/upstream/splat /app/splat
COPY --from=builder /data/sdf /data/sdf

RUN chown -R appuser:appuser /app /data/sdf

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
