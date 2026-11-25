"""A rock's outline, so the figure on an entry is the rock the field draws.

The field's vertex shader (site/static/field.js) picks one of eight outlines from
the seed column, mirrors half of them and gives each a starting turn. This module
states the same rule in Python: export.py writes seed(key) into the field file and
the entry page draws outline(key). tests/test_build.py checks that the two tables
below are the ones in field.js.
"""
from __future__ import annotations

import hashlib
import math

K = 12          # points per outline
SHAPES = 8
# Outline radii as a share of half the size: one row per shape, K points each.
RADII = (
    1.00, 0.78, 0.92, 0.70, 0.88, 0.97, 0.74, 0.90, 0.64, 0.86, 0.98, 0.80,
    0.92, 1.00, 0.70, 0.84, 0.96, 0.62, 0.88, 0.94, 0.76, 1.00, 0.68, 0.86,
    0.80, 0.96, 0.90, 0.58, 0.94, 0.86, 1.00, 0.72, 0.90, 0.66, 0.95, 0.88,
    1.00, 0.88, 0.64, 0.92, 0.98, 0.80, 0.60, 0.90, 0.96, 0.74, 0.86, 0.70,
    0.74, 0.94, 1.00, 0.82, 0.66, 0.96, 0.90, 0.70, 0.98, 0.84, 0.60, 0.92,
    0.90, 0.66, 0.98, 0.86, 0.94, 0.72, 1.00, 0.88, 0.62, 0.94, 0.80, 0.96,
    0.96, 0.84, 0.72, 1.00, 0.62, 0.90, 0.82, 0.97, 0.70, 0.92, 1.00, 0.66,
    0.68, 0.98, 0.86, 0.94, 0.76, 1.00, 0.66, 0.84, 0.96, 0.58, 0.90, 0.94,
)
SQUASH = (1, 0.82, 0.9, 0.74, 0.95, 0.7, 0.86, 0.78)   # each shape's width across its length


def seed(key: str) -> int:
    """The field file's seed column: 32 bits from the object key."""
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "little")


def outline(key: str) -> list[tuple[float, float]]:
    """K points with y running down the page, in units of half the rock's size.

    As the shader: shape seed % 8, mirrored when bit 3 is set, turned by bits 8-15
    as a share of a full turn.
    """
    s = seed(key)
    shape, mirror, turn = s % SHAPES, bool(s & 8), ((s >> 8) & 255) / 256.0
    cs, sn = math.cos(2 * math.pi * turn), math.sin(2 * math.pi * turn)
    pts = []
    for k in range(K):
        a = 2 * math.pi * k / K
        r = RADII[shape * K + k]
        x, y = r * math.cos(a), r * SQUASH[shape] * math.sin(a)
        if mirror:
            x = -x
        pts.append((cs * x - sn * y, -(sn * x + cs * y)))
    return pts
