"""Bounding boxes and clustering for motion mode (axis-aligned, legacy-style)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int
    members: list[int] = field(default_factory=list)
    label: tuple[str | None, float | None] = (None, None)


def aabb_gap(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> float:
    """Minimum gap between two axis-aligned boxes (0 if overlapping)."""
    x1, y1, w1, h1 = a
    x2, y2, w2, h2 = b
    dx = max(x1 - (x2 + w2), x2 - (x1 + w1), 0)
    dy = max(y1 - (y2 + h2), y2 - (y1 + h1), 0)
    return math.hypot(dx, dy)


def _union(a: BoundingBox, b: BoundingBox) -> BoundingBox:
    x = min(a.x, b.x)
    y = min(a.y, b.y)
    xr = max(a.x + a.w, b.x + b.w)
    yb = max(a.y + a.h, b.y + b.h)
    return BoundingBox(x, y, xr - x, yb - y, a.members + b.members, a.label)


def merge_boxes(boxes: list[BoundingBox], merge_dist: float = 75.0) -> list[BoundingBox]:
    """Merge boxes within merge_dist until stable (legacy DeepMeerkat used 75)."""
    if not boxes:
        return []
    while True:
        merged = False
        n = len(boxes)
        used = [False] * n
        out: list[BoundingBox] = []
        for i in range(n):
            if used[i]:
                continue
            cur = boxes[i]
            for j in range(i + 1, n):
                if used[j]:
                    continue
                bj = boxes[j]
                gap = aabb_gap((cur.x, cur.y, cur.w, cur.h), (bj.x, bj.y, bj.w, bj.h))
                if gap < merge_dist:
                    cur = _union(cur, boxes[j])
                    used[j] = True
                    merged = True
            out.append(cur)
        boxes = out
        if not merged:
            break
    return boxes


def contour_boxes(contours, bounding_rect_fn) -> list[BoundingBox]:
    boxes: list[BoundingBox] = []
    for i, c in enumerate(contours):
        x, y, w, h = bounding_rect_fn(c)
        boxes.append(BoundingBox(x, y, w, h, [i]))
    return merge_boxes(boxes)


def check_bounds(img, axis: int, p: int) -> int:
    if p > img.shape[axis]:
        return img.shape[axis]
    if p < 0:
        return 0
    return p


def mult(p: float, x: float) -> int:
    return int(p + p * x)


def resize_box_crop(img, bbox: BoundingBox, m: float = (math.sqrt(2) - 1) / 2):
    """Crop and resize to 299×299 (legacy training crop size)."""
    import cv2

    p1 = mult(bbox.y, -m)
    p1 = check_bounds(img, 0, p1)
    p2 = mult(bbox.y + bbox.h, m)
    p2 = check_bounds(img, 0, p2)
    p3 = mult(bbox.x, -m)
    p3 = check_bounds(img, 1, p3)
    p4 = mult(bbox.x + bbox.w, m)
    p4 = check_bounds(img, 1, p4)
    cropped = img[p1:p2, p3:p4]
    return cv2.resize(cropped, (299, 299))
