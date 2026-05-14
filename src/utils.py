import xml.etree.ElementTree as ET
from pathlib import Path
import arcade

from constants import HERO_PATH, HERO_ANIMATIONS_NEW, HERO_ANIMATIONS_OLD, DEFAULT_MAP_LAYER_OPTIONS


def load_animations(base_path: Path, animation_map: dict) -> dict:
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


def get_animation_map():
    if (HERO_PATH / "no_mowe_left").exists():
        return HERO_ANIMATIONS_NEW
    return HERO_ANIMATIONS_OLD


def load_layer_options_from_tmx(map_path: str) -> dict:
    tree = ET.parse(map_path)
    root = tree.getroot()
    options = {}
    for layer in root.findall("layer"):
        layer_name = layer.get("name")
        if layer_name:
            options[layer_name] = {"use_spatial_hash": layer_name == "Stop"}
    return options or DEFAULT_MAP_LAYER_OPTIONS.copy()
