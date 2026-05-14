import arcade
from PIL import ImageOps
from pathlib import Path
import argparse
from typing import Optional
import xml.etree.ElementTree as ET

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

PROJECT_ROOT = Path(__file__).resolve().parent
TEXTURE_ROOT = PROJECT_ROOT / "my_game_Texture"
if not TEXTURE_ROOT.exists():
    TEXTURE_ROOT = PROJECT_ROOT / "Valina_game_Texture"

MAP_PATH = TEXTURE_ROOT / "Location" / "Cave.tmx"

LEVEL_CONNECTIONS = {
    str(TEXTURE_ROOT / "Location" / "Cave.tmx"): {
        "left": {"map": str(TEXTURE_ROOT / "Location" / "Laibrery.tmx"), "spawn_x": "right_edge", "spawn_y": None},
    },
    str(TEXTURE_ROOT / "Location" / "Laibrery.tmx"): {
        "right": {"map": str(TEXTURE_ROOT / "Location" / "Cave.tmx"), "spawn_x": "left_edge", "spawn_y": None},
    },
}

DEFAULT_MAP_LAYER_OPTIONS = {
    "Flors": {"use_spatial_hash": True},
    "Stop": {"use_spatial_hash": True},
}

HERO_PATH = TEXTURE_ROOT / "hero"
ENEMY_PATH = TEXTURE_ROOT / "enemy"
GUN_PATH = TEXTURE_ROOT / "gun"
BULLET_PATH = GUN_PATH / "bullet"

HERO_ANIMATIONS_NEW = {
    "forward": "forward",
    "back": "back",
    "left": "left",
    "right": "right",
    "no_move_forward": "no_move_forward",
    "no_move_back": "no_move_back",
    "no_move_right": "no_move_right",
    "no_move_left": "no_mowe_left",
    "with_gun_forward": "with_gun_forward",
    "with_gun_back": "with_gun_back",
    "with_gun_right": "with_gun_right",
    "with_gun_left": "with_gun_left",
    "with_gun_no_move_forward": "with_gun_no_move_forward",
    "with_gun_no_move_back": "with_gun_no_move_back",
    "with_gun_no_move_right": "with_gun_no_move_right",
    "with_gun_no_move_left": "with_gun_no_move_left",
}

HERO_ANIMATIONS_OLD = {
    "forward": "forward",
    "back": "back",
    "left": "left",
    "right": "right",
    "no_move_forward": "no_move_forward",
    "no_move_back": "no_move_back",
    "no_move_right": "no_move_right",
    "no_move_left": "left",
    "with_gun_forward": "with_gun_forward",
    "with_gun_back": "with_gun_back",
    "with_gun_right": "with_gun_right",
    "with_gun_left": "with_gun_left",
    "with_gun_no_move_forward": "with_gun_forward",
    "with_gun_no_move_back": "with_gun_back",
    "with_gun_no_move_right": "with_gun_right",
    "with_gun_no_move_left": "with_gun_left",
}

ENEMY_ANIMATIONS = {
    "no_move_forward": "no_move_forward",
    "no_move_back": "no_move_back",
    "no_move_right": "no_move_right",
    "no_move_left": "no_move_left",
    "atack_forward": "atack_forward",
    "atack_back": "atack_back",
    "atack_right": "atack_right",
    "atack_left": "atack_left",
}


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


class Bullet(arcade.Sprite):
    def __init__(self, x, y, direction_x, direction_y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.change_x = direction_x * BULLET_SPEED
        self.change_y = direction_y * BULLET_SPEED
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.08
        self.scale = BULLET_SCALE
        self.lifetime = 0
        self.load_bullet_animation()

    def load_bullet_animation(self):
        bullet_frames = []
        if BULLET_PATH.exists():
            png_files = sorted(
                BULLET_PATH.glob("*.png"),
                key=lambda x: int(x.stem) if x.stem.isdigit() else 0
            )
            bullet_frames = [arcade.load_texture(str(f)) for f in png_files if f.name != "document.png"]

        if bullet_frames:
            self.texture = bullet_frames[0]
            self.frames = bullet_frames
        else:
            fallback = HERO_PATH / "bullet"
            if fallback.exists():
                png_files = sorted(
                    fallback.glob("*.png"),
                    key=lambda x: int(x.stem) if x.stem.isdigit() else 0
                )
                bullet_frames = [arcade.load_texture(str(f)) for f in png_files if f.name != "document.png"]
                if bullet_frames:
                    self.texture = bullet_frames[0]
                    self.frames = bullet_frames
                    return

            self.texture = arcade.make_circle_texture(8, (255, 255, 0, 255))
            self.frames = [self.texture]

    def update_animation(self, delta_time):
        if hasattr(self, 'frames') and len(self.frames) > 1:
            self.frame_timer += delta_time
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.texture = self.frames[self.current_frame]

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.lifetime += delta_time
        self.update_animation(delta_time)
        if self.lifetime > 1.2:
            self.remove_from_sprite_lists()


class Cherecters(arcade.Sprite):
    def __init__(self, is_hero=True):
        super().__init__()
        self.change_x = 0
        self.change_y = 0
        self.facing_direction = "forward"
        self.cur_texture = 0
        self.texture_timer = 0
        self.texture_scale = PLAYER_SCALE
        self.animations = {}
        self.has_gun = False
        self.is_hero = is_hero
        self._setup_animations()

    def _setup_animations(self):
        self.animations = {}
        if self.is_hero:
            anim_map = get_animation_map()
            self.animations = load_animations(HERO_PATH, anim_map)
        else:
            self.animations = load_animations(ENEMY_PATH, ENEMY_ANIMATIONS)

        if self.animations:
            available = list(self.animations.keys())
            fallback_key = available[0] if available else None
            first_anim = self.animations.get("no_move_forward") or self.animations.get("no_move_back") or (
                self.animations.get(fallback_key) if fallback_key else None
            )
            if first_anim:
                self.texture = arcade.load_texture(first_anim[0])
            else:
                self.texture = arcade.make_circle_texture(32, (100, 100, 255, 255))
        else:
            self.texture = arcade.make_circle_texture(32, (100, 100, 255, 255))
        self.scale = self.texture_scale

    def equip_gun(self):
        self.has_gun = True
        self.cur_texture = 0
        anim_map = get_animation_map()
        self.animations = load_animations(HERO_PATH, anim_map)
        self._set_texture_for_direction()

    def update_animation(self, delta_time: float = 0):
        self.texture_timer += delta_time
        if self.texture_timer >= 0.15:
            self.texture_timer = 0
            anim_key = self._get_animation_key()
            anim = self.animations.get(anim_key)
            frame_count = len(anim) if anim else 4
            self.cur_texture = (self.cur_texture + 1) % frame_count
            self._set_texture_for_direction()

    def _get_animation_key(self):
        is_moving = self.change_x != 0 or self.change_y != 0
        base_dir = self.facing_direction.replace("no_move_", "")

        if self.has_gun:
            if is_moving:
                return f"with_gun_{base_dir}"
            else:
                return f"with_gun_no_move_{base_dir}"
        else:
            return self.facing_direction

    def _set_texture_for_direction(self):
        is_moving = self.change_x != 0 or self.change_y != 0

        if is_moving:
            if self.change_x > 0:
                self.facing_direction = "right"
            elif self.change_x < 0:
                self.facing_direction = "left"
            elif self.change_y > 0:
                self.facing_direction = "forward"
            else:
                self.facing_direction = "back"
        else:
            if not self.facing_direction.startswith("no_move_"):
                self.facing_direction = "no_move_" + self.facing_direction

        base_dir = self.facing_direction.replace("no_move_", "")

        if self.has_gun:
            if is_moving:
                anim_key = f"with_gun_{base_dir}"
            else:
                anim_key = f"with_gun_no_move_{base_dir}"
        else:
            anim_key = self.facing_direction

        if anim_key not in self.animations:
            if is_moving:
                anim_key = base_dir
            else:
                anim_key = f"no_move_{base_dir}"

        if anim_key not in self.animations:
            available = [k for k in self.animations.keys() if self.animations[k]]
            if not available:
                self.texture = arcade.make_circle_texture(32, (100, 100, 255, 255))
                return
            anim_key = available[0]

        frames = self.animations[anim_key]
        if not frames:
            self.texture = arcade.make_circle_texture(32, (100, 100, 255, 255))
            return

        frame_path = frames[self.cur_texture % len(frames)]
        image = arcade.load_image(frame_path)
        self.texture = arcade.Texture(image)

    def update(self, delta_time: float = 0):
        self.center_x += self.change_x * MOVEMENT_SPEED
        self.center_y += self.change_y * MOVEMENT_SPEED


class Enemy(Cherecters):
    def __init__(self):
        super().__init__(is_hero=False)
        self.health = 100
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.is_attacking = False
        self.attack_direction = None

    def update(self, delta_time: float = 0):
        super().update(delta_time)
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.is_attacking = False
                self._set_texture_for_direction()

    def start_attack(self, direction):
        self.is_attacking = True
        self.attack_timer = 0.5
        self.attack_direction = direction

        if direction == "forward":
            self.facing_direction = "atack_forward"
        elif direction == "back":
            self.facing_direction = "atack_back"
        elif direction == "right":
            self.facing_direction = "atack_right"
        elif direction == "left":
            self.facing_direction = "atack_left"

        self.cur_texture = 0
        self._set_texture_for_direction()


class MyGame(arcade.Window):
    def __init__(self, width, height, title, map_path: str):
        super().__init__(width, height, title)
        layer_options = load_layer_options_from_tmx(map_path)
        self.map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.map)
        self.wall_list = self.map.sprite_lists.get("Stop", arcade.SpriteList())
        self.gun_list = self.map.sprite_lists.get("gun", arcade.SpriteList())
        self.gun_picked_up = False
        self.map_pixel_width = self.map.width * self.map.tile_width * TILE_SCALING
        self.map_pixel_height = self.map.height * self.map.tile_height * TILE_SCALING
        self.bullet_list = arcade.SpriteList()
        self.shoot_timer = 0
        self.camera = arcade.Camera2D(position=(width / 2, height / 2))
        self.ui_camera = arcade.Camera2D()
        self.hero = Cherecters(is_hero=True)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.hero)
        self.enemies = arcade.SpriteList()
        self.physics_engine = arcade.PhysicsEngineSimple(self.hero, self.wall_list)
        self.map_path = map_path

    def center_camera_to_player(self):
        half_w = self.width / 2
        half_h = self.height / 2
        min_x = half_w
        min_y = half_h
        max_x = max(half_w, self.map_pixel_width - half_w)
        max_y = max(half_h, self.map_pixel_height - half_h)
        cam_x, cam_y = self.camera.position
        dx = self.hero.center_x - cam_x
        dy = self.hero.center_y - cam_y

        target_x = cam_x
        target_y = cam_y
        if abs(dx) > CAMERA_DEADZONE_X:
            target_x = self.hero.center_x - CAMERA_DEADZONE_X * (1 if dx > 0 else -1)
        if abs(dy) > CAMERA_DEADZONE_Y:
            target_y = self.hero.center_y - CAMERA_DEADZONE_Y * (1 if dy > 0 else -1)

        target_x = min(max(target_x, min_x), max_x)
        target_y = min(max(target_y, min_y), max_y)

        self.camera.position = (
            cam_x + (target_x - cam_x) * CAMERA_SMOOTH,
            cam_y + (target_y - cam_y) * CAMERA_SMOOTH,
        )

    def shoot(self):
        if not self.hero.has_gun or self.shoot_timer > 0:
            return

        dx = 0
        dy = 0
        facing = self.hero.facing_direction
        if facing.startswith("no_move_"):
            facing = facing.replace("no_move_", "")

        if facing == "right":
            dx = 1
        elif facing == "left":
            dx = -1
        elif facing == "forward":
            dy = 1
        elif facing == "back":
            dy = -1

        bullet = Bullet(self.hero.center_x, self.hero.center_y, dx, dy)
        self.bullet_list.append(bullet)
        self.shoot_timer = SHOOT_DELAY

    def on_show(self):
        self.hero.center_x = self.map_pixel_width / 2
        self.hero.center_y = self.map_pixel_height / 2
        self.camera.position = (self.hero.center_x, self.hero.center_y)

    def load_level(self, map_path: str, spawn_x: Optional[float] = None, spawn_y: Optional[float] = None):
        self.map_path = map_path
        layer_options = load_layer_options_from_tmx(map_path)
        self.map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.map)
        self.wall_list = self.map.sprite_lists.get("Stop", arcade.SpriteList())
        self.gun_list = self.map.sprite_lists.get("gun", arcade.SpriteList())
        self.map_pixel_width = self.map.width * self.map.tile_width * TILE_SCALING
        self.map_pixel_height = self.map.height * self.map.tile_height * TILE_SCALING
        self.physics_engine = arcade.PhysicsEngineSimple(self.hero, self.wall_list)
        self.hero.center_x = spawn_x if spawn_x is not None else self.map_pixel_width / 2
        self.hero.center_y = spawn_y if spawn_y is not None else self.map_pixel_height / 2
        self.hero.change_x = 0
        self.hero.change_y = 0

    def on_update(self, delta_time):
        if self.shoot_timer > 0:
            self.shoot_timer -= delta_time

        self.physics_engine.update()

        if not self.hero.has_gun and not self.gun_picked_up and self.gun_list:
            for gun in self.gun_list:
                if arcade.check_for_collision(self.hero, gun):
                    gun.remove_from_sprite_lists()
                    self.hero.equip_gun()
                    self.gun_picked_up = True
                    break

        for bullet in list(self.bullet_list):
            bullet.update(delta_time)
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()

            for enemy in list(self.enemies):
                if arcade.check_for_collision(bullet, enemy):
                    bullet.remove_from_sprite_lists()
                    enemy.health -= 25
                    if enemy.health <= 0:
                        enemy.remove_from_sprite_lists()
                    break

        self.hero.update_animation(delta_time)
        self.hero.update(delta_time)

        for enemy in self.enemies:
            enemy.update(delta_time)

        self._check_level_transition()

        self.center_camera_to_player()

    def _draw_minimap(self):
        minimap_width = 150
        minimap_height = 100
        margin = 20
        minimap_x = margin
        minimap_y = self.height - minimap_height - margin

        scale_x = minimap_width / max(self.map_pixel_width, 1)
        scale_y = minimap_height / max(self.map_pixel_height, 1)

        arcade.draw_lbwh_rectangle_filled(minimap_x, minimap_y, minimap_width, minimap_height, (0, 0, 0, 180))
        arcade.draw_lbwh_rectangle_outline(minimap_x, minimap_y, minimap_width, minimap_height, (255, 255, 255, 200), 2)

        for wall in self.wall_list:
            wx = minimap_x + wall.center_x * scale_x
            wy = minimap_y + wall.center_y * scale_y
            ww = max(wall.width * scale_x, 1)
            wh = max(wall.height * scale_y, 1)
            arcade.draw_lbwh_rectangle_filled(wx, wy, ww, wh, (100, 100, 100, 150))

        for gun in self.gun_list:
            gx = minimap_x + gun.center_x * scale_x
            gy = minimap_y + gun.center_y * scale_y
            arcade.draw_circle_filled(gx, gy, 5, (255, 255, 0))

        hx = minimap_x + self.hero.center_x * scale_x
        hy = minimap_y + self.hero.center_y * scale_y
        arcade.draw_circle_filled(hx, hy, 4, (0, 255, 0))

    def _check_level_transition(self):
        current_map = self.map_path
        connections = LEVEL_CONNECTIONS.get(current_map, {})

        if not connections:
            return

        if self.hero.center_x < 0:
            direction = "left"
        elif self.hero.center_x > self.map_pixel_width:
            direction = "right"
        elif self.hero.center_y < 0:
            direction = "down"
        elif self.hero.center_y > self.map_pixel_height:
            direction = "up"
        else:
            return

        transition = connections.get(direction)
        if transition:
            next_map = transition["map"]
            spawn_x = transition.get("spawn_x")
            spawn_y = transition.get("spawn_y")
            if spawn_x == "left_edge":
                spawn_x = 100
            elif spawn_x == "right_edge":
                spawn_x = self.map_pixel_width - 100
            elif spawn_x is None:
                spawn_x = self.map_pixel_width / 2
            if spawn_y is None:
                spawn_y = self.map_pixel_height / 2
            self.map_path = next_map
            self.hero.center_x = spawn_x
            self.hero.center_y = spawn_y
            self._load_map(next_map)

    def _load_map(self, map_path: str):
        layer_options = load_layer_options_from_tmx(map_path)
        self.map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.map)
        self.wall_list = self.map.sprite_lists.get("Stop", arcade.SpriteList())
        self.gun_list = self.map.sprite_lists.get("gun", arcade.SpriteList())
        self.map_pixel_width = self.map.width * self.map.tile_width * TILE_SCALING
        self.map_pixel_height = self.map.height * self.map.tile_height * TILE_SCALING
        self.physics_engine = arcade.PhysicsEngineSimple(self.hero, self.wall_list)
        self.hero.change_x = 0
        self.hero.change_y = 0
        self.gun_picked_up = False

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.A:
            self.hero.change_x = -1
        elif symbol == arcade.key.D:
            self.hero.change_x = 1
        elif symbol == arcade.key.W:
            self.hero.change_y = 1
        elif symbol == arcade.key.S:
            self.hero.change_y = -1

        if symbol == arcade.key.SPACE and self.hero.has_gun and self.shoot_timer <= 0:
            self.shoot()

        self.hero._set_texture_for_direction()

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.A or symbol == arcade.key.D:
            self.hero.change_x = 0
        elif symbol == arcade.key.W or symbol == arcade.key.S:
            self.hero.change_y = 0
        self.hero._set_texture_for_direction()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.shoot_timer <= 0:
            self.shoot()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()

        if not self.gun_picked_up and self.gun_list:
            self.gun_list.draw()

        self.player_list.draw()
        self.bullet_list.draw()
        self.enemies.draw()

        self.ui_camera.use()
        self._draw_minimap()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default=MAP_PATH)
    args = parser.parse_args()
    map_path = Path(args.map)
    if not map_path.is_absolute():
        map_path = PROJECT_ROOT / map_path
    if not map_path.exists():
        raise FileNotFoundError(f"Не найден файл карты: {map_path}")

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Игра", str(map_path))
    arcade.run()


if __name__ == "__main__":
    main()