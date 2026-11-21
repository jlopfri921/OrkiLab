"""Project-scoped trainer dataset handoff without modifying shared trainer settings."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

# Image dataset Studio currently prepares flat image + caption pairs. Other
# modalities need their own preparation/validation profiles.
IMAGE_ENGINES = frozenset({
    "sdxl", "flux1", "flux3klein", "klein9b", "krea2", "qwenimage21",
    "qwenimage2512", "boogu", "zimage", "mingimage", "anima",
    "fibo2", "ernie", "mossimage", "ideogram4", "minimaxh3image",
})
HEX = set("0123456789abcdef")


class HandoffError(ValueError):
    pass


def project_data(base, project_id, engine_id):
    if not isinstance(project_id, str) or len(project_id) != 32 or not set(project_id) <= HEX:
        raise HandoffError("Invalid project identifier")
    base = Path(base)
    project_db = base / "settings" / "orkilab" / "projects.sqlite3"
    if not project_db.is_file():
        raise HandoffError("Project library is unavailable")
    with closing(sqlite3.connect(project_db)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id,name,engine,category,dataset FROM projects "
                           "WHERE id=? AND archived=0", (project_id,)).fetchone()
    if row is None:
        raise HandoffError("Project not found")
    project = dict(row)
    if project["engine"] != engine_id:
        raise HandoffError("Selected trainer does not match the project")
    # Prefer an explicitly prepared, internally-managed image/caption folder.
    path = None
    dataset_db = base / "settings" / "orkilab" / "datasets.sqlite3"
    if project["category"] == "image" and dataset_db.is_file():
        with closing(sqlite3.connect(dataset_db)) as conn:
            exists = conn.execute("SELECT 1 FROM sqlite_master "
                                  "WHERE type='table' AND name='dataset_preparations'").fetchone()
            if exists:
                row = conn.execute("SELECT path FROM dataset_preparations "
                                   "WHERE project_id=? ORDER BY rowid DESC LIMIT 1",
                                   (project_id,)).fetchone()
                if row:
                    path = row[0]
    if path:
        if engine_id not in IMAGE_ENGINES:
            raise HandoffError("This trainer needs a different dataset format; choose a compatible preparation")
        resolved = Path(path).resolve()
        allowed = (base / "Datasets" / "OrkiLab" / project_id).resolve()
        if allowed not in resolved.parents or not resolved.is_dir() or not (resolved / "manifest.json").is_file():
            raise HandoffError("Prepared dataset was moved or removed; prepare it again")
        # Ensure any replaced manifest is still associated with the project.
        try:
            manifest = json.loads((resolved / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("project_id") != project_id or manifest.get("format") != "flat_image_txt":
                raise HandoffError("Prepared dataset metadata is inconsistent")
        except (OSError, ValueError, TypeError) as exc:
            raise HandoffError("Cannot validate prepared dataset") from exc
        # A manifest bearing the correct project ID is not enough: reject
        # incomplete, traversing or replaced image/caption pairs before launch.
        items = manifest.get("items")
        if not isinstance(items, list) or not 0 < len(items) <= 200:
            raise HandoffError("Prepared dataset manifest has no valid image/caption entries")
        seen = set()
        for entry in items:
            if not isinstance(entry, dict):
                raise HandoffError("Prepared dataset manifest contains an invalid entry")
            image = entry.get("image")
            caption = entry.get("caption")
            if (not isinstance(image, str) or not isinstance(caption, str)
                    or not image or not caption or image in seen or caption in seen
                    or len(image) > 220 or len(caption) > 220
                    or Path(image).name != image or Path(caption).name != caption
                    or image in (".", "..") or caption in (".", "..")
                    or "\\" in image or "\\" in caption
                    or Path(image).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
                    or not caption.lower().endswith(".txt")
                    or Path(image).stem.casefold() != Path(caption).stem.casefold()):
                raise HandoffError("Prepared dataset manifest contains unsafe file names")
            seen.update((image, caption))
            for name in (image, caption):
                path_in_dataset = resolved / name
                if path_in_dataset.is_symlink() or not path_in_dataset.is_file():
                    raise HandoffError("Prepared dataset is incomplete; prepare it again")
                if not 0 < path_in_dataset.stat().st_size <= 40 * 1024 * 1024:
                    raise HandoffError("Prepared dataset file is empty or too large")
        project["selected_dataset"] = str(resolved)
        project["dataset_origin"] = "prepared"
    elif project["dataset"]:
        selected = Path(project["dataset"]).expanduser()
        if not selected.is_absolute() or not selected.is_dir():
            raise HandoffError("Project dataset folder does not exist; choose a valid absolute folder")
        project["selected_dataset"] = str(selected.resolve())
        project["dataset_origin"] = "project_path"
    else:
        raise HandoffError("No dataset linked to this project; prepare one in Dataset Studio")
    return project


def make_draft(base, project_id, engine_id):
    project = project_data(base, project_id, engine_id)
    config_folder = Path(base) / "settings"
    draft = {}
    for section, prefix in (("pre_cache", "pre_cache_settings_"),
                            ("train", "train_settings_")):
        cfg = config_folder / (prefix + engine_id + ".json")
        if cfg.is_file():
            try:
                saved = json.loads(cfg.read_text(encoding="utf-8"))
                if not isinstance(saved, dict):
                    raise HandoffError("Invalid trainer settings; cannot safely launch project")
            except (OSError, ValueError, TypeError) as exc:
                raise HandoffError("Cannot read trainer settings") from exc
        else:
            saved = {}
        saved["dataset_path"] = project["selected_dataset"]
        # Isolate default output/cache naming from existing projects.
        saved["project_name"] = "orkilab_" + project_id[:12]
        if engine_id == "minimaxh3image":
            saved["h3_model"] = "image"
        draft[section] = saved
    return draft, project
