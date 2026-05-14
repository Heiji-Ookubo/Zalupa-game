import xml.etree.ElementTree as ET

from constants import HERO_ANIMATIONS, DEFAULT_MAP_LAYER_OPTIONS


def load_animations(base_path, animation_map):
    animations = {}
    for key, folder_name in animation_map.items():
        anim_path = base_path / folder_name
        frames = []
        if anim_path.exists():
            png_files = sorted(
                anim_path.glob("*.png"),
                key=lambda x: int(x.stem) if x.stem.isdigit() else 0
            )
            frames = [str(f) for f in png_files if f.name != "document.png"]
        animations[key] = frames
    return animations


def load_layer_options_from_tmx(map_path: str) -> dict:
    tree = ET.parse(map_path)
    root = tree.getroot()
    options = {}
    for layer in root.findall("layer"):
        layer_name = layer.get("name")
        if layer_name:
            options[layer_name] = {"use_spatial_hash": layer_name == "Stop"}
    return options or DEFAULT_MAP_LAYER_OPTIONS.copy()
