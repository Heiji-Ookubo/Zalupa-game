from pathlib import Path
import arcade

#Для настройки всех констант
SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()
MOVEMENT_SPEED = 5
TILE_SCALING = 1.0
TILE_SIZE = 32
PLAYER_SCALE = 1.4
CAMERA_SMOOTH = 0.14
CAMERA_DEADZONE_X = 140
CAMERA_DEADZONE_Y = 90

BULLET_SPEED = 20
SHOOT_DELAY = 0.3
BULLET_SCALE = 3

ENEMY_SPEED = 4
ENEMY_DETECT_RANGE = 600
ENEMY_ATTACK_RANGE = 40
ENEMY_ATTACK_COOLDOWN = 1.0
ENEMY_DAMAGE = 30
ENEMY_BULLET_SPEED = 7
ENEMY_BULLET_DAMAGE = 10
ENEMY_RANGED_COOLDOWN = 1.0
ENEMY_RANGED_RANGE = 600
ENEMY_BULLET_LIFETIME = 2.0

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEXTURE_ROOT = PROJECT_ROOT / "texture"

MAP_PATH = TEXTURE_ROOT / "location" / "cave.tmx"

LEVEL_CONNECTIONS = {
    str(TEXTURE_ROOT / "location" / "cave.tmx"): {
        "left": {"map": str(TEXTURE_ROOT / "location" / "Library.tmx"), "spawn_x": "right_edge", "spawn_y": None},
    },
    str(TEXTURE_ROOT / "location" / "Library.tmx"): {
        "right": {"map": str(TEXTURE_ROOT / "location" / "cave.tmx"), "spawn_x": "left_edge", "spawn_y": None},
    },
}

DEFAULT_MAP_LAYER_OPTIONS = {
    "Flors": {"use_spatial_hash": True},
    "Stop": {"use_spatial_hash": True},
}

HERO_PATH = TEXTURE_ROOT / "hero"
ENEMY_PATH = TEXTURE_ROOT / "enemy"
SPIRIT_BOL_PATH = ENEMY_PATH / "spirit_bol"
GUN_PATH = TEXTURE_ROOT / "gun"
BULLET_PATH = GUN_PATH / "bullet"

HERO_ANIMATIONS = {
    "forward": "forward",
    "back": "back",
    "left": "left",
    "right": "right",
    "no_move_forward": "no_move_forward",
    "no_move_back": "no_move_back",
    "no_move_right": "no_move_right",
    "no_move_left": "no_move_left",
    "with_gun_forward": "with_gun_forward",
    "with_gun_back": "with_gun_back",
    "with_gun_right": "with_gun_right",
    "with_gun_left": "with_gun_left",
    "with_gun_no_move_forward": "with_gun_no_move_forward",
    "with_gun_no_move_back": "with_gun_no_move_back",
    "with_gun_no_move_right": "with_gun_no_move_right",
    "with_gun_no_move_left": "with_gun_no_move_left",
}

ENEMY_ANIMATIONS = {
    "forward": "no_move_forward",
    "back": "no_move_back",
    "right": "no_move_right",
    "left": "no_move_left",
    "no_move_forward": "no_move_forward",
    "no_move_back": "no_move_back",
    "no_move_right": "no_move_right",
    "no_move_left": "no_move_left",
    "atack_forward": "atack_forward",
    "atack_back": "atack_back",
    "atack_right": "atack_right",
    "atack_left": "atack_left",
}
