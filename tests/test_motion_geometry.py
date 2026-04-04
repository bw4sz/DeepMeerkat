import numpy as np

from deepmeerkat.motion_geometry import BoundingBox, aabb_gap, contour_boxes, merge_boxes


def test_aabb_gap_overlap() -> None:
    assert aabb_gap((0, 0, 10, 10), (5, 5, 10, 10)) == 0.0


def test_merge_boxes() -> None:
    boxes = [
        BoundingBox(0, 0, 10, 10, [0]),
        BoundingBox(12, 0, 10, 10, [1]),
    ]
    merged = merge_boxes(boxes, merge_dist=5.0)
    assert len(merged) == 1


def test_contour_boxes() -> None:
    import cv2

    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (40, 40), 255, -1)
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = contour_boxes(contours, cv2.boundingRect)
    assert len(boxes) >= 1
