#!/usr/bin/env python

import sys
import os
from pmtiles.tile import zxy_to_tileid, TileType, Compression
from pmtiles.writer import Writer

if len(sys.argv) != 3:
    print("Usage: cterrain2pmtiles TILESET_DIR PMTILES_FILE")
    exit(1)

tileset_dir = sys.argv[1]
pmtiles_file = sys.argv[2]

# tileset_dir = "/var/www/static.mah.priv.at/tilesets/si-20m/"
# pmtiles_file = "si.pmtiles"


def tile_gen(root):
    for path, _, filenames in os.walk(root):
        for file in filenames:
            if file.endswith(".terrain"):
                pn = os.path.join(path, file)
                (z, x, y) = [
                    int(v)
                    for v in pn.removeprefix(root).removesuffix(".terrain").split("/")
                ]
                # yield f"{z=} {x=} {y=} {pn=}"
                yield (z, x, y, pn)


tiles = tile_gen(tileset_dir)
acc = 0

with open(pmtiles_file, "wb") as f:
    writer = Writer(f)
    for z, x, y, terrain_tile in tile_gen(tileset_dir):
        try:
            tileid = zxy_to_tileid(z, x, y)
            with open(terrain_tile, "rb") as t:
                writer.write_tile(tileid, t.read())
        except ValueError as e:
            print(e, f"{z=} {x=} {y=} {terrain_tile=}")
            if x > 2 ^ z - 1:
                print("x too large")
            if y > 2 ^ z - 1:
                print("y too large")

    writer.finalize(
        # this does not make sense yet
        {
            "tile_type": TileType.PNG,
            "tile_compression": Compression.NONE,
            "min_zoom": 0,
            "max_zoom": 3,
            "min_lon_e7": int(-180.0 * 10000000),
            "min_lat_e7": int(-85.0 * 10000000),
            "max_lon_e7": int(180.0 * 10000000),
            "max_lat_e7": int(85.0 * 10000000),
            "center_zoom": 0,
            "center_lon_e7": 0,
            "center_lat_e7": 0,
        },
        {
            "attribution": 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
        },
    )
sys.exit(0)
