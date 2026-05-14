import math
import arcade

from constants import (
    PLAYER_SCALE, MOVEMENT_SPEED, HERO_PATH, ENEMY_PATH, ENEMY_ANIMATIONS,
    HERO_ANIMATIONS,
    ENEMY_SPEED, ENEMY_DETECT_RANGE, ENEMY_ATTACK_RANGE, ENEMY_ATTACK_COOLDOWN,
    ENEMY_RANGED_COOLDOWN, ENEMY_RANGED_RANGE,
)
from utils import load_animations
from bullet import EnemyBullet


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
        self.health = 100
        self.is_hero = is_hero
        self.speed = MOVEMENT_SPEED
        self._setup_animations()

    def _setup_animations(self):
        self.animations = {}
        if self.is_hero:
            self.animations = load_animations(HERO_PATH, HERO_ANIMATIONS)
        else:
            self.animations = load_animations(ENEMY_PATH, ENEMY_ANIMATIONS)

        if self.animations:
            available = list(self.animations.keys())
            first_anim = self.animations.get("no_move_forward") or self.animations.get("no_move_back") or (
                self.animations.get(available[0]) if available else None
            )
            if first_anim:
                self.texture = arcade.load_texture(first_anim[0])
        self.scale = self.texture_scale

    def equip_gun(self):
        self.has_gun = True
        self.cur_texture = 0
        self.animations = load_animations(HERO_PATH, HERO_ANIMATIONS)
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
        self._update_facing()
        anim_key = self._resolve_anim_key()
        self._apply_animation(anim_key)

    def _update_facing(self):
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
        elif not self.facing_direction.startswith("no_move_"):
            self.facing_direction = "no_move_" + self.facing_direction

    def _resolve_anim_key(self):
        is_moving = self.change_x != 0 or self.change_y != 0
        base = self.facing_direction.replace("no_move_", "")

        if self.has_gun:
            key = f"with_gun_{base}" if is_moving else f"with_gun_no_move_{base}"
        else:
            key = self.facing_direction

        if key in self.animations:
            return key

        key = base if is_moving else f"no_move_{base}"
        if key in self.animations:
            return key

        available = [k for k in self.animations if self.animations[k]]
        return available[0] if available else None

    def _apply_animation(self, anim_key):
        if not anim_key:
            return
        frames = self.animations.get(anim_key)
        if not frames:
            return
        frame_path = frames[self.cur_texture % len(frames)]
        image = arcade.load_image(frame_path)
        self.texture = arcade.Texture(image)

    def update(self, delta_time: float = 0):
        self.center_x += self.change_x * self.speed
        self.center_y += self.change_y * self.speed


class Enemy(Cherecters):
    def __init__(self):
        super().__init__(is_hero=False)
        self.health = 100
        self.attack_timer = 0
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
        self.attack_cooldown_timer = 0
        self.is_attacking = False
        self.attack_direction = None
        self.damage_dealt = False
        self.speed = ENEMY_SPEED
        self.target = None
        self.detect_range = ENEMY_DETECT_RANGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.ranged_range = ENEMY_RANGED_RANGE
        self.ranged_cooldown_timer = 0
        self.bullet_list = None

    def shoot_at(self, target_x, target_y):
        if self.bullet_list is None:
            return
        bullet = EnemyBullet(self.center_x, self.center_y, target_x, target_y)
        self.bullet_list.append(bullet)
        self.ranged_cooldown_timer = ENEMY_RANGED_COOLDOWN

    def _set_texture_for_direction(self):
        self._update_facing()
        anim_key = self._resolve_anim_key()
        self._apply_animation(anim_key)

    def _update_facing(self):
        is_moving = self.change_x != 0 or self.change_y != 0
        if is_moving and not self.is_attacking:
            if abs(self.change_x) >= abs(self.change_y):
                self.facing_direction = "right" if self.change_x > 0 else "left"
            else:
                self.facing_direction = "forward" if self.change_y > 0 else "back"

    def _resolve_anim_key(self):
        is_moving = self.change_x != 0 or self.change_y != 0
        if self.facing_direction in self.animations:
            return self.facing_direction
        base = self.facing_direction.replace("no_move_", "")
        key = base if is_moving else f"no_move_{base}"
        if key in self.animations:
            return key
        available = [k for k in self.animations if self.animations[k]]
        return available[0] if available else None

    def update(self, delta_time: float = 0):
        super().update(delta_time)
        self._update_timers(delta_time)
        self._decide_action()

    def _update_timers(self, delta_time):
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self._end_attack()

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= delta_time

        if self.ranged_cooldown_timer > 0:
            self.ranged_cooldown_timer -= delta_time

    def _end_attack(self):
        self.is_attacking = False
        self.attack_cooldown_timer = self.attack_cooldown
        if self.attack_direction:
            self.facing_direction = self.attack_direction
        self._set_texture_for_direction()

    def _decide_action(self):
        if not self.target or self.is_attacking or self.attack_cooldown_timer > 0:
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist >= self.detect_range:
            self.change_x = 0
            self.change_y = 0
            return

        if dist < self.attack_range:
            self._melee_attack(dx, dy)
        elif dist < self.ranged_range and self.ranged_cooldown_timer <= 0:
            self._ranged_attack()
        else:
            self._chase(dx, dy, dist)

    def _melee_attack(self, dx, dy):
        self.change_x = 0
        self.change_y = 0
        direction = "right" if abs(dx) > abs(dy) else "forward"
        if direction == "right":
            direction = "right" if dx > 0 else "left"
        else:
            direction = "forward" if dy > 0 else "back"
        self.start_attack(direction)

    def _ranged_attack(self):
        self.change_x = 0
        self.change_y = 0
        self.shoot_at(self.target.center_x, self.target.center_y)

    def _chase(self, dx, dy, dist):
        self.change_x = dx / dist
        self.change_y = dy / dist

    def start_attack(self, direction):
        self.is_attacking = True
        self.attack_timer = 0.5
        self.attack_direction = direction
        self.damage_dealt = False

        if direction == "forward":
            self.facing_direction = "atack_forward"
        elif direction == "back":
            self.facing_direction = "atack_back"
        elif direction == "right":
            self.facing_direction = "atack_right"
        elif direction == "left":
            self.facing_direction = "atack_left"

        self.cur_texture = 0
        anim_key = self.facing_direction
        frames = self.animations.get(anim_key)
        if frames:
            frame_path = frames[self.cur_texture % len(frames)]
            image = arcade.load_image(frame_path)
            self.texture = arcade.Texture(image)
