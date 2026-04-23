import arcade
from pyglet.event import EVENT_HANDLE_STATE

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 980
MOVEMENT_SPEED = 3

class Cherecters(arcade.Sprite):

    def __init__(self,*image_paths: str):
        super().__init__(image_paths[0])
        self.change_x = 0
        self.change_y = 0

    def update(self,delta_time:float=0):
        self.position_x += self.change_x * MOVEMENT_SPEED
        self.position_y += self.change_y * MOVEMENT_SPEED

class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)
        self.uebok = Cherecters("zalupa/бездействие.gif")
        self.plyer_list = arcade.SpriteList()
        self.plyer_list.append(self.uebok)
        arcade.set_background_color(arcade.color.ASH_GREY)

    def on_show(self) -> EVENT_HANDLE_STATE:
        self.uebok.position_x = self.width/2
        self.uebok.position_y = self.height/2

    def on_update(self, delta_time):
        self.uebok.update()

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.A:
            self.uebok.change_x = -1
        elif key == arcade.key.D:
            self.uebok.change_x = 1
        elif key == arcade.key.W:
            self.uebok.change_y = 1
        elif key == arcade.key.S:
            self.uebok.change_y = -1

    def on_key_release(self, key, modifiers):
        """ Called whenever a user releases a key. """
        if key == arcade.key.A or key == arcade.key.D:
            self.uebok.change_x = 0
        elif key == arcade.key.W or key == arcade.key.S:
            self.uebok.change_y = 0

def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Пример рисования")

    arcade.run()


main()