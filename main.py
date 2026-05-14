import arcade
from PIL import ImageOps
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET
import math

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()
MOVEMENT_SPEED = 5
TILE_SCALING = 2.0
TILE_SIZE = 32
PLAYER_SCALE = 1.4
CAMERA_SMOOTH = 0.14
CAMERA_DEADZONE_X = 140
CAMERA_DEADZONE_Y = 90

BULLET_SPEED = 20
SHOOT_DELAY = 0.3
BULLET_SCALE = 7

PROJECT_ROOT = Path(__file__).resolve().parent
TEXTURE_ROOT = PROJECT_ROOT / "my_game_Texture"
if not TEXTURE_ROOT.exists():
    TEXTURE_ROOT = PROJECT_ROOT / "Valina_game_Texture"
BASE_PATH = TEXTURE_ROOT / "hero"
MAP_PATH = TEXTURE_ROOT / "Location/Cave.tmx"
DEFAULT_MAP_LAYER_OPTIONS = {
    "Flors": {"use_spatial_hash": True},
    "Stop": {"use_spatial_hash": True},
}


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
        """Загрузка анимации пули из папки героя"""
        try:
            bullet_frames = []
            bullet_path = BASE_PATH / "bullet"
            if bullet_path.exists():
                for i in range(1, 5):
                    frame_path = bullet_path / f"{i}.png"
                    if frame_path.exists():
                        frame = arcade.load_texture(str(frame_path))
                        bullet_frames.append(frame)
                if bullet_frames:
                    self.texture = bullet_frames[0]
                    self.frames = bullet_frames
                    return
        except:
            pass
        self.texture = arcade.make_circle_texture(8, (255, 255, 0))
        self.frames = [self.texture]

    def update_animation(self, delta_time):
        """Обновление анимации пули"""
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


def load_layer_options_from_tmx(map_path: str) -> dict[str, dict[str, bool]]:
    tree = ET.parse(map_path)
    root = tree.getroot()
    options = {}
    for layer in root.findall("layer"):
        layer_name = layer.get("name")
        if layer_name:
            options[layer_name] = {"use_spatial_hash": layer_name == "Stop"}
    return options or DEFAULT_MAP_LAYER_OPTIONS.copy()


class Cherecters(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.change_x = 0
        self.change_y = 0
        self.facing_direction = "forward"
        self.cur_texture = 0
        self.texture_timer = 0
        self.texture_scale = PLAYER_SCALE
        self.animations = {}
        self.has_gun = False
        self._setup_animations()

    def _setup_animations(self):
        self.animations = {
            "forward": [str(BASE_PATH / "forward" / f"{i}.png") for i in range(1, 5)],
            "back": [str(BASE_PATH / "back" / f"{i}.png") for i in range(1, 5)],
            "right": [str(BASE_PATH / "right" / f"{i}.png") for i in range(1, 5)],
            "no_move_forward": [str(BASE_PATH / "no_move_forward" / f"{i}.png") for i in range(1, 5)],
            "no_move_back": [str(BASE_PATH / "no_move_back" / f"{i}.png") for i in range(1, 5)],
            "no_move_right": [str(BASE_PATH / "no_move_right" / f"{i}.png") for i in range(1, 5)],
            "with_gun_forward": [str(BASE_PATH / "with_gun_forward" / f"{i}.png") for i in range(1, 5)],
            "with_gun_back": [str(BASE_PATH / "with_gun_back" / f"{i}.png") for i in range(1, 5)],
            "with_gun_right": [str(BASE_PATH / "with_gun_right" / f"{i}.png") for i in range(1, 5)],
            "with_gun_left": [str(BASE_PATH / "with_gun_left" / f"{i}.png") for i in range(1, 5)],
        }
        self.texture = arcade.load_texture(self.animations["no_move_forward"][0])
        self.scale = self.texture_scale

    def equip_gun(self):
        self.has_gun = True
        self.cur_texture = 0
        self._set_texture_for_direction()

    def update_animation(self, delta_time: float = 0):
        self.texture_timer += delta_time
        if self.texture_timer >= 0.15:
            self.texture_timer = 0
            self.cur_texture = (self.cur_texture + 1) % 4
            self._set_texture_for_direction()

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

        flip_x = False
        if self.facing_direction.startswith("no_move_"):
            if self.facing_direction == "no_move_left":
                base_direction = "no_move_right"
                flip_x = True
            else:
                base_direction = self.facing_direction
        elif self.has_gun:
            if self.facing_direction == "left":
                base_direction = "with_gun_left"
            elif self.facing_direction == "right":
                base_direction = "with_gun_right"
            elif self.facing_direction == "forward":
                base_direction = "with_gun_forward"
            else:
                base_direction = "with_gun_back"
        elif self.facing_direction == "left":
            base_direction = "right"
            flip_x = True
        else:
            base_direction = self.facing_direction

        if flip_x:
            image = ImageOps.mirror(arcade.load_image(self.animations[base_direction][self.cur_texture]))
        else:
            image = arcade.load_image(self.animations[base_direction][self.cur_texture])
        self.texture = arcade.Texture(image)

    def update(self, delta_time: float = 0):
        self.center_x += self.change_x * MOVEMENT_SPEED
        self.center_y += self.change_y * MOVEMENT_SPEED


class MyGame(arcade.Window):
    def __init__(self, width, height, title, map_path: str):
        super().__init__(width, height, title)
        layer_options = load_layer_options_from_tmx(map_path)
        self.map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.map)
        self.wall_list = self.map.sprite_lists.get("Stop", arcade.SpriteList())
        self.gun_list = self.map.sprite_lists.get("gun", arcade.SpriteList())
        self.camera = arcade.Camera2D(position=(width / 2, height / 2))
        self.hero = Cherecters()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.hero)
        self.physics_engine = arcade.PhysicsEngineSimple(self.hero, self.wall_list)
        self.map_pixel_width = self.map.width * self.map.tile_width * TILE_SCALING
        self.map_pixel_height = self.map.height * self.map.tile_height * TILE_SCALING
        self.bullet_list = arcade.SpriteList()
        self.shoot_timer = 0
        self.gun_picked_up = False

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
        """Метод для стрельбы"""
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

        for bullet in self.bullet_list[:]:
            bullet.update(delta_time)

            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()

        self.hero.update_animation(delta_time)
        self.hero.update(delta_time)
        self.center_camera_to_player()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.hero.change_x = -1
        elif key == arcade.key.D:
            self.hero.change_x = 1
        elif key == arcade.key.W:
            self.hero.change_y = 1
        elif key == arcade.key.S:
            self.hero.change_y = -1

        if key == arcade.key.SPACE and self.shoot_timer <= 0:
            self.shoot()

        self.hero._set_texture_for_direction()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.hero.change_x = 0
        elif key == arcade.key.W or key == arcade.key.S:
            self.hero.change_y = 0
        self.hero._set_texture_for_direction()

    def on_mouse_press(self, x, y, button, modifiers):
        """Стрельба по ЛКМ"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.shoot_timer <= 0:
            self.shoot()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()

        # Рисуем пистолеты на земле (если они еще есть)
        if not self.gun_picked_up and self.gun_list:
            self.gun_list.draw()

        self.player_list.draw()
        self.bullet_list.draw()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--map",
        default=MAP_PATH,
    )
    args = parser.parse_args()
    map_path = Path(args.map)
    if not map_path.is_absolute():
        map_path = PROJECT_ROOT / map_path
    if not map_path.exists():
        raise FileNotFoundError(f"Не найден файл карты: {map_path}")

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Тимофей, ты валыну то убери", str(map_path))
    arcade.run()


if __name__ == "__main__":
    main()