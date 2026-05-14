import math
from pathlib import Path
import arcade

from constants import (
    BULLET_PATH, BULLET_SPEED, BULLET_SCALE, HERO_PATH,
    SPIRIT_BOL_PATH, ENEMY_BULLET_SPEED, ENEMY_BULLET_DAMAGE, ENEMY_BULLET_LIFETIME,
)


def _collect_pngs(path: Path):
    if not path.exists():
        return []
    png_files = sorted(
        path.glob("*.png"),
        key=lambda x: int(x.stem) if x.stem.isdigit() else 0
    )
    return [arcade.load_texture(str(f)) for f in png_files if f.name != "document.png"]


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
        frames = _collect_pngs(BULLET_PATH)
        if not frames:
            frames = _collect_pngs(HERO_PATH / "bullet")
        if frames:
            self.texture = frames[0]
            self.frames = frames

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


class EnemyBullet(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.change_x = (dx / dist) * ENEMY_BULLET_SPEED
            self.change_y = (dy / dist) * ENEMY_BULLET_SPEED
        else:
            self.change_x = 0
            self.change_y = 0
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.1
        self.lifetime = 0
        self.damage = ENEMY_BULLET_DAMAGE
        self.load_textures()

    def load_textures(self):
        frames = _collect_pngs(SPIRIT_BOL_PATH)
        if frames:
            self.texture = frames[0]
            self.frames = frames
        self.scale = 2

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
        if self.lifetime > ENEMY_BULLET_LIFETIME:
            self.remove_from_sprite_lists()
