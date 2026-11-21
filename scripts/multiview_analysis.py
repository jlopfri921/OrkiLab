"""Deterministic orientation and quality hints for Multiview Studio alpha.2.

Azimuth is manually provided metadata; a bin is NOT a claim of 3D reconstruction
or full surface visibility. Rejected captures never count as coverage.
Sharpness is a heuristic, not proof of image focus or suitability.
"""
from collections import Counter, defaultdict

SECTORS = 12
SECTOR_WIDTH_DEG = 360 // SECTORS
MIN_SHORT_EDGE = 512
POSSIBLY_BLURRY_BELOW = 8.0
MAX_CAPTURE_POINTS = 5000


def angle_sector(azimuth):
    if azimuth is None:
        return None
    return int((float(azimuth) + SECTOR_WIDTH_DEG / 2) // SECTOR_WIDTH_DEG) % SECTORS


def analyze(rows):
    """Return project-scoped, all-pages report for records from one subject.

    rows: capture records, no media read and no mutation. The caller must
    scope the SQL query to a verified project and subject.
    """
    total = len(rows)
    bins = [dict(center_deg=i * SECTOR_WIDTH_DEG, count=0,
                 approved=0, provisional=0, capture_ids=[])
            for i in range(SECTORS)]
    sha_groups = defaultdict(list)
    reviewed = Counter()
    unknown_angles = 0
    rejected_with_angles = 0
    captures = []
    blur_hints = 0
    low_resolution_hints = 0
    sharpness_unavailable = 0
    for row in rows:
        r = dict(row)
        status = r["review"]
        reviewed[status] += 1
        sha_groups[r["sha256"]].append(r["id"])
        angle = r["azimuth_deg"]
        if angle is None:
            unknown_angles += 1
        elif status == "rejected":
            rejected_with_angles += 1
        else:
            sector = bins[angle_sector(angle)]
            sector["count"] += 1
            sector["capture_ids"].append(r["id"])
            sector["approved" if status == "approved" else "provisional"] += 1
        low_res = min(r["width"], r["height"]) < MIN_SHORT_EDGE
        low_resolution_hints += int(low_res)
        score = r.get("sharpness_score")
        blurry = score is not None and score < POSSIBLY_BLURRY_BELOW
        blur_hints += int(blurry)
        sharpness_unavailable += int(score is None)
        if len(captures) < MAX_CAPTURE_POINTS:
            captures.append(dict(
                id=r["id"], name=r["view_name"] or r["name"],
                view_name=r["view_name"], source_type=r["source_type"],
                review=status, azimuth_deg=angle, elevation_deg=r["elevation_deg"],
                distance_m=r["distance_m"], width=r["width"], height=r["height"],
                sharpness_score=score, possibly_blurry=blurry,
                low_resolution=low_res,
                sector_center_deg=None if angle is None else angle_sector(angle) * SECTOR_WIDTH_DEG,
            ))
    duplicates = [ids for ids in sha_groups.values() if len(ids) > 1]
    duplicate_ids = {i for group in duplicates for i in group}
    for entry in captures:
        entry["exact_duplicate"] = entry["id"] in duplicate_ids
    occupied = [b["center_deg"] for b in bins if b["count"]]
    approved = [b["center_deg"] for b in bins if b["approved"]]
    return dict(
        total=total, sectors=bins, occupied_sectors=occupied,
        missing_sectors=[b["center_deg"] for b in bins if not b["count"]],
        coverage_percent=round(100 * len(occupied) / SECTORS, 1),
        approved_coverage_percent=round(100 * len(approved) / SECTORS, 1),
        unknown_angles=unknown_angles,
        rejected_with_angles=rejected_with_angles,
        reviews=dict(unreviewed=reviewed["unreviewed"],
                     approved=reviewed["approved"], rejected=reviewed["rejected"]),
        quality=dict(low_resolution=low_resolution_hints,
                     possibly_blurry=blur_hints,
                     sharpness_unavailable=sharpness_unavailable,
                     exact_duplicate_groups=duplicates,
                     exact_duplicate_captures=len(duplicate_ids)),
        captures=captures, limited=total > MAX_CAPTURE_POINTS,
        method=dict(sectors=SECTORS, width_deg=SECTOR_WIDTH_DEG,
                    alignment="nearest 30-degree center",
                    coverage="azimuth bins only; manual/estimated metadata, not validated geometry",
                    small_image_short_edge_below=MIN_SHORT_EDGE,
                    blurry_hint_score_below=POSSIBLY_BLURRY_BELOW)
    )
