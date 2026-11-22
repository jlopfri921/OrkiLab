# Dataset Studio 0.4.0-alpha.1 — development closeout

**Date:** 2026-11-21  
**Status:** **CODE COMPLETE / CI PASS; ON-DEVICE VISUAL ACCEPTANCE NOT VERIFIED.** This is a development checkpoint, **not** a tagged, published or fully accepted 0.4 prerelease. Do not confuse passing automated tests with a manually confirmed Windows browser session.

## Delivered to main

- PR [#46](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/46): dedicated `/workspace/datasets` entry; project-linked local image index and image previews; non-destructive import/removal; SQLite reference store; local-only API and fixture tests.
- PR [#47](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/pull/47): image dimensions (best-effort header parser), filename/size/resolution ordering, text/review filters, multiple selection, approved/rejected/unreviewed states, confirmed bulk reference removal, browser locale labels in eight languages and regression tests.
- The published `v0.3.0-rc.1` tag is unchanged. Alpha.1 is only in ongoing `main` development.

## Automated acceptance

| Gate | Status | Evidence / limitation |
| --- | --- | --- |
| Windows Python tests, PR #47 | PASS | Both GitHub Actions test workflows succeeded on PR head before merge |
| Ubuntu Python tests, PR #47 | PASS | Both workflows succeeded on PR head before merge |
| Exact merge commit `fc0b045b4dd0952bba0a0959d2c154b17505feee` | PASS | [RC validation](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/actions/runs/44882947004) and [foundation checks](https://github.com/jlopfri921/OrkiLab-LoRA-TrainerStudio/actions/runs/44882947077), both successful |
| Non-destructive images and repeat import | PASS (fixture) | Automated tests verify original image bytes and idempotent reference import |
| Bulk status updates, deletion of index references, filters, dimensions and schema upgrade | PASS (fixture) | No original file operations; missing indexed files handled |
| Local-only access, cross-origin mutations and malformed batch inputs | PASS (focused tests) | Not a full hostile-browser or network security audit |
| Real Windows browser layout at desktop/mobile widths | **NOT VERIFIED** | No direct access to the operator's Windows desktop/browser |
| Manual images import/search/review/delete on original real dataset | **NOT VERIFIED** | Cannot infer physical acceptance from CI |
| All format variants, large libraries, performance and corrupted media safety | **NOT VERIFIED** | Must be checked on real datasets; best-effort image metadata is not full format decoding |

## Windows operator smoke checklist (not yet claimed as passed)

1. Update local checkout from `main`, restart launcher, open `http://127.0.0.1:4990/workspace/datasets`.
2. Select an image-category project, import a folder of 15–20 JPG/PNG/WebP files, including one nonimage and one missing/broken entry if possible.
3. Confirm thumbnails, dimensions where supported, filtering, sorting, selected count, approving/rejecting/resetting and empty/missing-file states.
4. Remove several references (with confirmation); verify physically that original image files and bytes remain unchanged.
5. Check keyboard interaction, desktop/mobile width layout, language changes, responsiveness and browser console errors. Record Windows version, browser, commit SHA and a result for each test.

**Exit rule:** Code work is closed; label the alpha milestone **fully accepted** only when the missing browser and local-dataset checks are actually recorded. Discovered failures become follow-up PRs rather than silently reclassifying the checks as PASS.

## Next milestone

Proceed with `0.4.0-alpha.2` as a separate branch for deterministic exact-file duplicate detection and image-quality indicators, with bounded/cancellable scans, preview before any action, and no source modification. The open operator checks above remain visible until completed.
