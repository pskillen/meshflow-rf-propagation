#!/usr/bin/env python3
"""Pre-compute UK-overlapping SRTM tiles as SPLAT .sdf files under SDF_BAKE_OUT."""

from __future__ import annotations

import os
import sys


def main() -> None:
    upstream = os.environ["UPSTREAM_ROOT"]
    splat_path = os.environ["SPLAT_PREFIX"]
    out_dir = os.environ.get("SDF_BAKE_OUT", "/data/sdf")

    if upstream not in sys.path:
        sys.path.insert(0, upstream)

    from app.services.splat import Splat

    def iter_tiles():
        for lat_tile in range(49, 62):
            for lon_tile in range(-11, 3):
                ns = "N" if lat_tile >= 0 else "S"
                ew = "E" if lon_tile >= 0 else "W"
                tile_name = f"{ns}{abs(lat_tile):02d}{ew}{abs(lon_tile):03d}.hgt.gz"
                sdf_name = Splat._hgt_filename_to_sdf_filename(tile_name, False)
                sdf_hd_name = Splat._hgt_filename_to_sdf_filename(tile_name, True)
                yield tile_name, sdf_name, sdf_hd_name

    os.makedirs(out_dir, exist_ok=True)

    splat = Splat(
        splat_path=splat_path,
        cache_dir=os.path.join(out_dir, ".tile_cache"),
    )

    done: set[str] = set()
    failed: list[str] = []

    for tile_name, sdf_name, _sdf_hd in iter_tiles():
        if sdf_name in done:
            continue
        dest = os.path.join(out_dir, sdf_name)
        if os.path.isfile(dest):
            print(f"skip existing {dest}", flush=True)
            done.add(sdf_name)
            continue
        try:
            tile_data = splat._download_terrain_tile(tile_name)
            sdf_data = splat._convert_hgt_to_sdf(
                tile_data, tile_name, high_resolution=False
            )
        except Exception as exc:
            print(f"skip {tile_name}: {exc}", flush=True)
            failed.append(tile_name)
            continue
        with open(dest, "wb") as fh:
            fh.write(sdf_data)
        done.add(sdf_name)
        print(dest, flush=True)

    if not done:
        raise SystemExit(
            "No .sdf tiles were produced; check network access to terrain S3."
        )
    print(
        f"Baked {len(done)} tiles to {out_dir}; "
        f"skipped missing tiles: {len(failed)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
