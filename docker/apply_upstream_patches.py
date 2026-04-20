#!/usr/bin/env python3
"""Apply Meshflow-specific patches to a cloned meshtastic-site-planner tree."""

from __future__ import annotations

import sys
from pathlib import Path


def patch_main(root: Path) -> None:
    path = root / "app" / "main.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "import logging\nimport io\n# import os\n",
        "import logging\nimport io\nimport os\n",
        1,
    )
    text = text.replace(
        'redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=False)',
        'redis_client = redis.StrictRedis.from_url(\n'
        '    os.environ.get("REDIS_URL", "redis://redis:6379/0"),\n'
        "    decode_responses=False,\n"
        ")",
        1,
    )
    path.write_text(text, encoding="utf-8")


def patch_splat(root: Path) -> None:
    path = root / "app" / "services" / "splat.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "import os\nimport io\n",
        "import os\nimport shutil\nimport io\n",
        1,
    )
    old_loop = """                # download and convert terrain tiles to SPLAT! sdf
                for tile_name, sdf_name, sdf_hd_name in required_tiles:
                    tile_data = self._download_terrain_tile(tile_name)
                    sdf_data = self._convert_hgt_to_sdf(tile_data, tile_name, high_resolution=request.high_resolution)

                    with open(os.path.join(tmpdir, sdf_hd_name if request.high_resolution else sdf_name), "wb") as sdf_file:
                        sdf_file.write(sdf_data)
"""
    new_loop = """                # download and convert terrain tiles to SPLAT! sdf
                for tile_name, sdf_name, sdf_hd_name in required_tiles:
                    sdf_basename = sdf_hd_name if request.high_resolution else sdf_name
                    sdf_dir = os.environ.get("SDF_DIR")
                    baked_path = (
                        os.path.join(sdf_dir, sdf_basename)
                        if sdf_dir
                        else None
                    )
                    if baked_path and os.path.isfile(baked_path):
                        logger.info("Using baked terrain tile from %s", baked_path)
                        shutil.copy2(baked_path, os.path.join(tmpdir, sdf_basename))
                        continue

                    tile_data = self._download_terrain_tile(tile_name)
                    sdf_data = self._convert_hgt_to_sdf(tile_data, tile_name, high_resolution=request.high_resolution)

                    with open(os.path.join(tmpdir, sdf_basename), "wb") as sdf_file:
                        sdf_file.write(sdf_data)
"""
    if old_loop not in text:
        raise SystemExit("patch_splat: expected loop block not found (upstream changed?)")
    text = text.replace(old_loop, new_loop, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    patch_main(root)
    patch_splat(root)
    print(f"Patched upstream tree at {root}")


if __name__ == "__main__":
    main()
