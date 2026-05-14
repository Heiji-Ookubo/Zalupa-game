from typing import Optional
import arcade

from constants import (
    SHOOT_DELAY, TILE_SCALING, LEVEL_CONNECTIONS, ENEMY_DAMAGE, ENEMY_BULLET_DAMAGE,
    CAMERA_SMOOTH, CAMERA_DEADZONE_X, CAMERA_DEADZONE_Y,
)
from characters import Cherecters, Enemy
from bullet import Bullet, EnemyBullet
from utils import load_layer_options_from_tmx


class MyGame(arcade.Window):
    def __init__(self, width, height, title, map_path: str):
        super().__init__(width, height, title)
        self.bullet_list = arcade.SpriteList()
        self.shoot_timer = 0
        self.camera = arcade.Camera2D(position=(width / 2, height / 2))
        self.ui_camera = arcade.Camera2D()
        self.hero = Cherecters(is_hero=True)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.hero)
        self.enemies = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.map_path = map_path
        self._setup_level(map_path)

    def _setup_level(self, map_path: str, spawn_x: Optional[float] = None, spawn_y: Optional[float] = None):
        self.map_path = map_path
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
        if spawn_x is not None:
            self.hero.center_x = spawn_x
        if spawn_y is not None:
            self.hero.center_y = spawn_y

        self.enemies.clear()
        self.enemy_bullet_list.clear()
        enemy_objects = self.map.object_lists.get("enemy", [])
        for obj in enemy_objects:
            if isinstance(obj.shape, list) and len(obj.shape) == 4:
                xs = [p[0] for p in obj.shape]
                ys = [p[1] for p in obj.shape]
                enemy = Enemy()
                enemy.center_x = (min(xs) + max(xs)) / 2
                enemy.center_y = (min(ys) + max(ys)) / 2
                enemy.target = self.hero
                enemy.bullet_list = self.enemy_bullet_list
                self.enemies.append(enemy)

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

        for bullet in list(self.enemy_bullet_list):
            bullet.update(delta_time)
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision(bullet, self.hero):
                self.hero.health -= bullet.damage
                bullet.remove_from_sprite_lists()

        for enemy in self.enemies:
            enemy.update(delta_time)
            enemy.update_animation(delta_time)
            if enemy.is_attacking and not enemy.damage_dealt and arcade.check_for_collision(enemy, self.hero):
                enemy.damage_dealt = True
                self.hero.health -= ENEMY_DAMAGE

        if self.hero.health <= 0:
            self.close()
            return

        self._check_level_transition()
        self.center_camera_to_player()

    def _draw_hp(self):
        hp_width = 200
        hp_height = 20
        hp_x = self.width - hp_width - 20
        hp_y = self.height - 40

        arcade.draw_lbwh_rectangle_filled(hp_x, hp_y, hp_width, hp_height, (60, 60, 60))
        ratio = max(self.hero.health / 100, 0)
        color = (255, 50, 50) if ratio < 0.3 else (255, 200, 50) if ratio < 0.6 else (50, 200, 50)
        arcade.draw_lbwh_rectangle_filled(hp_x, hp_y, hp_width * ratio, hp_height, color)
        arcade.draw_lbwh_rectangle_outline(hp_x, hp_y, hp_width, hp_height, (255, 255, 255, 200), 2)
        arcade.draw_text(f"HP: {int(self.hero.health)}", hp_x + 5, hp_y + 2, (255, 255, 255), 12)

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

        if not self.hero.has_gun and not self.gun_picked_up:
            for gun in self.gun_list:
                gx = minimap_x + gun.center_x * scale_x
                gy = minimap_y + gun.center_y * scale_y
                arcade.draw_circle_filled(gx, gy, 5, (255, 255, 0))

        for enemy in self.enemies:
            ex = minimap_x + enemy.center_x * scale_x
            ey = minimap_y + enemy.center_y * scale_y
            arcade.draw_circle_filled(ex, ey, 4, (255, 0, 0))

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
        if not transition:
            return

        next_map = transition["map"]
        spawn_x = transition.get("spawn_x")
        spawn_y = transition.get("spawn_y")

        self._load_map(next_map)

        if spawn_x == "left_edge":
            self.hero.center_x = 100
        elif spawn_x == "right_edge":
            self.hero.center_x = self.map_pixel_width - 100
        elif spawn_x is None:
            self.hero.center_x = self.map_pixel_width / 2

        if spawn_y is None:
            self.hero.center_y = self.map_pixel_height / 2

    def _load_map(self, map_path: str, spawn_x: Optional[float] = None, spawn_y: Optional[float] = None):
        self._setup_level(map_path, spawn_x, spawn_y)

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

        for name in list(self.scene._name_mapping.keys()):
            if name != "gun":
                self.scene._name_mapping[name].draw()

        if not self.hero.has_gun and not self.gun_picked_up and self.gun_list:
            self.gun_list.draw()

        self.player_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.enemies.draw()

        self.ui_camera.use()
        self._draw_minimap()
        self._draw_hp()
