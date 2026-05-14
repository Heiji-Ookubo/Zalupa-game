import argparse
from pathlib import Path
import arcade

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PROJECT_ROOT, MAP_PATH
from game_window import MyGame

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
