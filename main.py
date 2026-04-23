import arcade
from PIL import ImageOps

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 980
MOVEMENT_SPEED = 10

BASE_PATH = "Zalupa_game_Texture/hero"


class Cherecters(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.change_x = 0
        self.change_y = 0
        self.facing_direction = "forward"
        self.cur_texture = 0
        self.texture_timer = 0
        self.texture_scale = 4
        self.animations = {}
        self._setup_animations()

    def _setup_animations(self):
        self.animations = {
            "forward": [f"{BASE_PATH}/forward/{i}.png" for i in range(1, 5)],
            "back": [f"{BASE_PATH}/back/{i}.png" for i in range(1, 5)],
            "right": [f"{BASE_PATH}/right/{i}.png" for i in range(1, 5)],
            "no_move_forward": [f"{BASE_PATH}/no_move_forward/{i}.png" for i in range(1, 5)],
            "no_move_back": [f"{BASE_PATH}/no_move_back/{i}.png" for i in range(1, 5)],
            "no_move_right": [f"{BASE_PATH}/no_move_right/{i}.png" for i in range(1, 5)],
        }
        self.texture = arcade.load_texture(self.animations["no_move_forward"][0])

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
        if self.facing_direction in ("no_move_left", "left"):
            base_direction = "right" if self.facing_direction == "left" else "no_move_right"
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
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.uebok = Cherecters()
        self.plyer_list = arcade.SpriteList()
        self.plyer_list.append(self.uebok)
        arcade.set_background_color(arcade.color.ASH_GREY)

    def on_show(self):
        self.uebok.center_x = self.width / 2
        self.uebok.center_y = self.height / 2

    def on_update(self, delta_time):
        self.uebok.update_animation(delta_time)
        self.uebok.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.uebok.change_x = -1
        elif key == arcade.key.D:
            self.uebok.change_x = 1
        elif key == arcade.key.W:
            self.uebok.change_y = 1
        elif key == arcade.key.S:
            self.uebok.change_y = -1

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.uebok.change_x = 0
        elif key == arcade.key.W or key == arcade.key.S:
            self.uebok.change_y = 0

    def on_draw(self):
        self.clear()
        self.plyer_list.draw()


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Пример рисования")
    arcade.run()


if __name__ == "__main__":
    main()