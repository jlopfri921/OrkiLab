"""Conservative conversion of ordinary ComfyUI visual graphs.

Only known built-in widget layouts are converted. Unknown frontend behavior,
subgraphs, bypasses and custom widgets require an API export from ComfyUI.
"""
from urllib.parse import quote

# Explicit frontend widget order, including seed control widgets.
LAYOUTS = {
    "CheckpointLoaderSimple": ("ckpt_name",),
    "CLIPTextEncode": ("text",),
    "EmptyLatentImage": ("width", "height", "batch_size"),
    "KSampler": ("seed", None, "steps", "cfg", "sampler_name", "scheduler", "denoise"),
    "VAEDecode": (),
    "VAEEncode": (),
    "SaveImage": ("filename_prefix",),
    "PreviewImage": (),
    "LoraLoader": ("lora_name", "strength_model", "strength_clip"),
    "LoraLoaderModelOnly": ("lora_name", "strength_model"),
    "VAELoader": ("vae_name",),
    "CLIPSetLastLayer": ("stop_at_clip_layer",),
    "LoadImage": ("image", None),
}

def node_schema(url, kind, get_json):
    for prefix in ("/object_info/", "/api/object_info/"):
        try:
            data = get_json(url, prefix + quote(kind, safe=""), max_bytes=8_000_000, timeout=20)
            if isinstance(data, dict) and isinstance(data.get(kind), dict):
                return data[kind]
        except (OSError, ValueError):
            pass
    raise ValueError("Node metadata unavailable: " + kind)

def combo_choices(descriptor):
    """Return an explicit finite option list for legacy and V3 ComfyUI COMBOs.

    None means there is no recognized/usable dropdown schema. Never accept
    arbitrary scalars when an advertised options list is missing or invalid.
    """
    if not isinstance(descriptor, list) or not descriptor:
        return None
    typ = descriptor[0]
    if isinstance(typ, list):
        choices = typ
    elif typ == "COMBO":
        opts = descriptor[1] if len(descriptor) > 1 else None
        choices = opts.get("options") if isinstance(opts, dict) else None
    else:
        return None
    if (not isinstance(choices, list) or not 0 < len(choices) <= 5000
            or any(type(x) not in (str, int, float, bool) for x in choices)):
        return None
    return choices


def validate_prompt(prompt, schema):
    for ident, node in prompt.items():
        kind = node["class_type"]
        spec = schema[kind]
        fields = spec.get("input", {})
        required = dict(fields.get("required", {}))
        optional = dict(fields.get("optional", {}))
        # ComfyUI V3 DynamicCombo is a scalar option key, not a link socket.
        # Only the selected option's explicitly declared nested inputs exist.
        for parent, desc in tuple(required.items()) + tuple(optional.items()):
            if not isinstance(desc, list) or not desc or desc[0] != "COMFY_DYNAMICCOMBO_V3":
                continue
            meta = desc[1] if len(desc) > 1 and isinstance(desc[1], dict) else {}
            options = meta.get("options")
            selected = node["inputs"].get(parent)
            if (not isinstance(selected, str) or not isinstance(options, list)
                    or not 0 < len(options) <= 100
                    or any(not isinstance(o, dict) or not isinstance(o.get("key"), str)
                           for o in options)):
                raise ValueError(f"{kind} #{ident}: invalid dynamic dropdown for {parent}")
            matches = [o for o in options if o["key"] == selected]
            if len(matches) != 1:
                raise ValueError(f"{kind} #{ident}: unavailable dynamic option {parent}: {selected}")
            nested = matches[0].get("inputs")
            if not isinstance(nested, dict):
                raise ValueError(f"{kind} #{ident}: invalid dynamic option metadata for {parent}")
            for target, section in ((required, nested.get("required", {})),
                                    (optional, nested.get("optional", {}))):
                if not isinstance(section, dict) or len(section) > 64:
                    raise ValueError(f"{kind} #{ident}: invalid dynamic input schema for {parent}")
                for child, descriptor in section.items():
                    if (not isinstance(child, str) or not child or "." in child
                            or child == parent or not isinstance(descriptor, list)
                            or not descriptor or parent + "." + child in required
                            or parent + "." + child in optional):
                        raise ValueError(f"{kind} #{ident}: invalid nested input {parent}")
                    target[parent + "." + child] = descriptor
        for name in required:
            if name not in node["inputs"]:
                raise ValueError(f"{kind} #{ident}: missing input {name}")
        for name, value in node["inputs"].items():
            descriptor = required.get(name, optional.get(name))
            if not isinstance(descriptor, list) or not descriptor:
                raise ValueError(f"{kind} #{ident}: unknown input {name}")
            typ = descriptor[0]
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str) and type(value[1]) is int:
                upstream = prompt.get(value[0])
                if upstream is None:
                    raise ValueError(f"{kind} #{ident}: invalid link {name}")
                outputs = schema[upstream["class_type"]].get("output", [])
                if not 0 <= value[1] < len(outputs):
                    raise ValueError(f"{kind} #{ident}: invalid output slot")
                if isinstance(typ, str) and typ not in ("*", outputs[value[1]]):
                    raise ValueError(f"{kind} #{ident}: incompatible link {name}")
                continue
            if typ == "COMFY_DYNAMICCOMBO_V3":
                # Option and selected child fields were validated above.
                continue
            if isinstance(typ, list) or typ == "COMBO":
                choices = combo_choices(descriptor)
                if choices is None:
                    raise ValueError(f"{kind} #{ident}: invalid dropdown metadata for {name}")
                if not any(type(value) is type(option) and value == option for option in choices):
                    raise ValueError(f"{kind} #{ident}: unavailable option {name}: {value}")
                continue
            if typ == "INT" and type(value) is not int:
                raise ValueError(f"{kind} #{ident}: invalid integer {name}")
            if typ == "FLOAT" and type(value) not in (int, float):
                raise ValueError(f"{kind} #{ident}: invalid number {name}")
            if typ == "STRING" and not isinstance(value, str):
                raise ValueError(f"{kind} #{ident}: invalid text {name}")
            if typ == "BOOLEAN" and type(value) is not bool:
                raise ValueError(f"{kind} #{ident}: invalid boolean {name}")
            if isinstance(typ, str) and typ not in ("INT","FLOAT","STRING","BOOLEAN","*","COMBO"):
                # A scalar may be valid in a different node version, but the
                # *connected* ComfyUI node schema is authoritative. Do not
                # silently coerce a sampler selector into an object link.
                if kind == "KSamplerSelect" and name == "sampler_name":
                    raise ValueError(
                        f"{kind} #{ident}: sampler_name is {typ!r} in the connected ComfyUI "
                        f"node schema but the workflow supplies a scalar. "
                        "Check whether a custom node overrides KSamplerSelect, "
                        "or export the workflow again from this ComfyUI installation "
                        "in API format. A SAMPLER-type input needs a real node link."
                    )
                raise ValueError(f"{kind} #{ident}: input {name} requires a link (ComfyUI type: {typ})")
            opts = descriptor[1] if len(descriptor) > 1 and isinstance(descriptor[1], dict) else {}
            if type(value) in (int,float) and (("min" in opts and value < opts["min"]) or ("max" in opts and value > opts["max"])):
                raise ValueError(f"{kind} #{ident}: out of range {name}")
    if not any(schema[n["class_type"]].get("output_node") for n in prompt.values()):
        raise ValueError("No executable output node")
    visiting, done = set(), set()
    def visit(ident):
        if ident in visiting:
            raise ValueError("Workflow contains a cycle")
        if ident in done:
            return
        visiting.add(ident)
        for v in prompt[ident]["inputs"].values():
            if isinstance(v,list) and len(v)==2 and isinstance(v[0],str):
                visit(v[0])
        visiting.remove(ident)
        done.add(ident)
    for ident in prompt:
        visit(ident)

def convert_visual(graph, url, get_json):
    nodes = graph.get("nodes")
    links = graph.get("links")
    if not isinstance(nodes,list) or not isinstance(links,list):
        raise ValueError("Unsupported visual graph structure")
    definitions = graph.get("definitions") or {}
    if not isinstance(definitions, dict):
        raise ValueError("Unsupported workflow definitions")
    subgraphs = definitions.get("subgraphs") or []
    if not isinstance(subgraphs, list):
        raise ValueError("Unsupported subgraph definitions")
    subgraph_ids = {str(item.get("id")) for item in subgraphs if isinstance(item, dict)}
    used = [n for n in nodes if str(n.get("type")) in subgraph_ids]
    if used:
        names = {str(item.get("id")): str(item.get("name") or item.get("id")) for item in subgraphs if isinstance(item, dict)}
        raise ValueError("Subgraphs require ComfyUI API export: " + ", ".join(names[str(n.get("type"))] for n in used)[:300])
    if any(value for key, value in definitions.items() if key != "subgraphs"):
        raise ValueError("Unsupported workflow definitions")
    link_map = {}
    for link in links:
        if not isinstance(link,list) or len(link)<6 or type(link[2]) is not int or type(link[4]) is not int:
            raise ValueError("Unsupported link format")
        if str(link[0]) in link_map:
            raise ValueError("Duplicate link ID")
        link_map[str(link[0])] = (str(link[1]),link[2],str(link[3]),link[4])
    prompt, schemas = {}, {}
    for n in nodes:
        kind = n.get("type")
        if kind in ("Note","MarkdownNote") and not n.get("inputs") and not n.get("outputs"):
            continue
        if n.get("mode",0) != 0 or kind not in LAYOUTS:
            raise ValueError(f"Unsupported visual node: {kind}. Export API format in ComfyUI.")
        ident = str(n.get("id"))
        if ident in prompt or ident=="None":
            raise ValueError("Invalid node ID")
        if kind not in schemas:
            schemas[kind] = node_schema(url,kind,get_json)
        widgets = n.get("widgets_values",[])
        layout = LAYOUTS[kind]
        if not isinstance(widgets,list) or len(widgets)!=len(layout):
            raise ValueError(f"{kind}: unsupported widget layout")
        inputs = {name: value for name,value in zip(layout,widgets) if name is not None}
        for i, slot in enumerate(n.get("inputs",[])):
            if not isinstance(slot,dict) or not isinstance(slot.get("name"),str):
                raise ValueError("Invalid input slot")
            if slot.get("link") is None:
                continue
            link = link_map.get(str(slot["link"]))
            if not link or link[2:] != (ident,i):
                raise ValueError("Invalid visual link")
            inputs[slot["name"]] = [link[0],link[1]]
        prompt[ident] = {"class_type":kind,"inputs":inputs}
    validate_prompt(prompt,schemas)
    return prompt
