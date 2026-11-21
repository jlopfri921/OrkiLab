"""Read-only ComfyUI connection, configured on the launcher host."""
import ipaddress
import json
import os
import tempfile
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
import socket
from urllib.request import build_opener, ProxyHandler, HTTPRedirectHandler
from flask import jsonify, request

DEFAULT = "http://127.0.0.1:8188"
MODES = ("native", "comfy", "hybrid")

def validate_settings(body, previous):
    if not isinstance(body, dict):
        raise ValueError("Invalid request")
    mode = body.get("mode", previous["mode"])
    if mode not in MODES:
        raise ValueError("Invalid engine mode")
    folder = body.get("model_folder", previous["model_folder"])
    if not isinstance(folder, str) or len(folder) > 1024 or any(ord(c) < 32 for c in folder):
        raise ValueError("Invalid model folder")
    lora_folder = body.get("lora_folder", previous.get("lora_folder", ""))
    if not isinstance(lora_folder, str) or len(lora_folder) > 1024 or any(ord(c) < 32 for c in lora_folder):
        raise ValueError("Invalid ComfyUI LoRA folder")
    result = {"mode": mode, "url": validate_url(body.get("url", previous["url"])),
              "model_folder": folder.strip(), "lora_folder": lora_folder.strip()}
    return result

DEFAULT_SETTINGS = {"mode": "hybrid", "url": DEFAULT, "model_folder": "", "lora_folder": ""}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def validate_url(value):
    if not isinstance(value, str) or len(value) > 200:
        raise ValueError("Invalid ComfyUI address")
    try:
        u = urlsplit(value.strip())
        host = u.hostname
        ip = ipaddress.ip_address("127.0.0.1" if host == "localhost" else host or "")
        port = u.port or (443 if u.scheme == "https" else 80)
        allowed = any(ip in ipaddress.ip_network(n) for n in (
            "127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
            "100.64.0.0/10", "::1/128", "fc00::/7"))
        if (u.scheme not in ("http", "https") or not allowed or u.username is not None
                or u.password is not None or u.path not in ("", "/") or u.query or u.fragment
                or not 1 <= port <= 65535 or "%" in u.netloc):
            raise ValueError()
        address = "[" + str(ip) + "]" if ip.version == 6 else str(ip)
        return f"{u.scheme}://{address}:{port}"
    except (ValueError, TypeError):
        raise ValueError("Use a local or private IP address and port")

def get_json(base, path, max_bytes=2_000_000, timeout=4):
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(base + path, timeout=timeout) as response:
        raw = response.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError("Response too large")
    return json.loads(raw)

def probe(base):
    stats = get_json(base, "/system_stats")
    if not isinstance(stats, dict) or not isinstance(stats.get("system"), dict) or not isinstance(stats.get("devices"), list):
        raise ValueError("Not a ComfyUI response")
    system = stats["system"]
    return {"connected": True, "version": str(system.get("comfyui_version", ""))[:100],
            "devices": [str(d.get("name", ""))[:200] for d in stats["devices"][:16] if isinstance(d, dict)]}

def register(app, base):
    file = base / "settings" / "orkilab" / "comfyui.json"

    def load():
        try:
            return validate_settings(json.loads(file.read_text(encoding="utf-8")), DEFAULT_SETTINGS)
        except (OSError, ValueError, KeyError, TypeError):
            return dict(DEFAULT_SETTINGS)

    @app.route("/api/workspace/comfyui", methods=["GET", "POST"])
    def comfyui_settings():
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Configure ComfyUI on the launcher PC"), 403
        if request.method == "GET":
            return jsonify(load())
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 4096:
            return jsonify(error="Invalid request"), 400
        body = request.get_json(silent=True)
        try:
            config = validate_settings(body, load())
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=file.parent, delete=False) as tmp:
            json.dump(config, tmp)
            name = tmp.name
        try:
            os.replace(name, file)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        return jsonify(config)

    @app.post("/api/workspace/comfyui/check")
    def comfyui_check():
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Configure ComfyUI on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 1024:
            return jsonify(error="Invalid request"), 400
        try:
            config = load()
            if config["mode"] == "native":
                return jsonify(error="ComfyUI is disabled in native mode"), 409
            return jsonify(probe(config["url"]))
        except (OSError, ValueError):
            return jsonify(connected=False, error="Could not connect to ComfyUI"), 502

    @app.post("/api/workspace/models")
    def workspace_models():
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Configure ComfyUI on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 1024:
            return jsonify(error="Invalid request"), 400
        from model_inventory import inventory
        return jsonify(inventory(base, load(), get_json))

    @app.post("/api/workspace/comfyui/nodes")
    def comfyui_nodes():
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify(error="Configure ComfyUI on the launcher PC"), 403
        if request.mimetype != "application/json" or not 0 < (request.content_length or 0) <= 1024:
            return jsonify(error="Invalid request"), 400
        config = load()
        if config["mode"] == "native":
            return jsonify(error="ComfyUI is disabled in native mode"), 409
        from comfyui_nodes import fetch_nodes
        try:
            return jsonify(fetch_nodes(config["url"], get_json))
        except HTTPError as exc:
            return jsonify(error="Could not read ComfyUI nodes", detail=f"HTTP {exc.code}", endpoint=config["url"] + "/object_info"), 502
        except (TimeoutError, socket.timeout):
            return jsonify(error="Could not read ComfyUI nodes", detail="Timeout (60 s)", endpoint=config["url"] + "/object_info"), 502
        except URLError as exc:
            return jsonify(error="Could not read ComfyUI nodes", detail=str(exc.reason)[:300], endpoint=config["url"] + "/object_info"), 502
        except (OSError, ValueError) as exc:
            return jsonify(error="Could not read ComfyUI nodes", detail=str(exc)[:300], endpoint=config["url"] + "/object_info"), 502
