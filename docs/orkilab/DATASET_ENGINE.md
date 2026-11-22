# Dataset engine — proposed

Existing dataset manager, caption scripts and Dataset Forge already cover captions, reference generation and facial likeness. Extend rather than replace.

Manifest schema v1: project ID, source path, SHA256, media type, width/height, origin (real/synthetic), caption, trigger, license/consent, optional yaw/pitch/roll and camera provenance, quality flags and split. Store relative paths; keep original files immutable. Import preview before applying changes. Dedup exact hashes then image pHash; optional embeddings for near duplicates. Flag blur, low resolution and inconsistent aspect ratios; manual overrides auditable. Split by source identity/near-duplicate cluster to prevent leakage. Record generated vs reference views. Synthetic occluded surfaces are estimates, not ground truth.

Profiles: person, fictional character, object, sculpture, vehicle, architecture, style, paired edit. Face matching only for appropriate authorized people, not sculptures; optional model license constraints apply. Validate with held-out reference data; captions describe variable features rather than inadvertently baking them into identity. For multiview require independent left/right and consistent framing. No source upload by default.

Acceptance: manifests reproducible; no deletion of originals; duplicate test fixtures; angle and synthetic labels survive export; privacy review.
