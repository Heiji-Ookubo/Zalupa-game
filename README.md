# 👻 Zalupa Game

2D top-down игра на Python + Arcade. Герой бродит по пещерам и библиотекам,
находит пистолет, отбивается от призраков и переходит между уровнями.

---

## 🗂️ Структура проекта

```
Zalupa-game/
├── README.md
├── src/
│   ├── main.py             # Точка входа — запуск игры
│   ├── constants.py        # Все настройки, пути, анимации
│   ├── utils.py            # Утилиты: загрузка анимаций и карт
│   ├── bullet.py           # Классы пуль (герой + враг)
│   ├── characters.py       # Классы персонажей (герой + враг)
│   └── game_window.py      # Окно игры — вся логика и отрисовка
└── texture/
    ├── hero/               # Спрайты героя
    │   ├── forward/ etc    #   движение
    │   ├── no_move_*/      #   покой
    │   └── with_gun_*/     #   с пистолетом
    ├── enemy/              # Спрайты призрака
    │   ├── no_move_*/      #   покой
    │   ├── atack_*/        #   атака
    │   └── spirit_bol/     #   огненные шары
    ├── gun/                # Пистолет и патроны
    │   ├── gun/            #   пистолет на полу
    │   └── bullet/         #   пули
    └── location/           # Карты уровней
        ├── cave.tmx        #   пещера (старт)
        ├── Library.tmx     #   библиотека
        ├── *.tsx           #   тайловые наборы
        └── Tail/           #   текстуры тайлов
```

---

## ⚙️ constants.py — Настройки

Константы вынесены отдельно, чтобы не искать их по коду.

### Экран и камера

| Константа | Значение | Описание |
|---|---|---|
| `SCREEN_WIDTH/HEIGHT` | `arcade.get_display_size()` | Размер экрана |
| `MOVEMENT_SPEED` | 5 | Скорость героя |
| `TILE_SCALING` | 1.0 | Масштаб тайлов |
| `PLAYER_SCALE` | 1.4 | Масштаб спрайта героя |
| `CAMERA_SMOOTH` | 0.14 | Плавность камеры |
| `CAMERA_DEADZONE_X/Y` | 140/90 | Мёртвая зона камеры |

### Пули героя

| Константа | Значение | Описание |
|---|---|---|
| `BULLET_SPEED` | 20 | Скорость пули |
| `SHOOT_DELAY` | 0.3 | Секунд между выстрелами |
| `BULLET_SCALE` | 3 | Размер пули |

### Призрак (Enemy)

| Константа | Значение | Описание |
|---|---|---|
| `ENEMY_SPEED` | 4 | Скорость призрака |
| `ENEMY_DETECT_RANGE` | 600 | Радиус обнаружения героя |
| `ENEMY_ATTACK_RANGE` | 40 | Дистанция для удара |
| `ENEMY_ATTACK_COOLDOWN` | 1.0 | Перезарядка удара (сек) |
| `ENEMY_DAMAGE` | 30 | Урон от удара |
| `ENEMY_BULLET_SPEED` | 7 | Скорость огненного шара |
| `ENEMY_BULLET_DAMAGE` | 10 | Урон от шара |
| `ENEMY_RANGED_COOLDOWN` | 1.0 | Перезарядка выстрела (сек) |
| `ENEMY_RANGED_RANGE` | 600 | Дальность стрельбы |
| `ENEMY_BULLET_LIFETIME` | 2.0 | Время жизни шара (сек) |

### Пути к текстурам

```
PROJECT_ROOT = zalupa-game/
TEXTURE_ROOT = zalupa-game/texture/

MAP_PATH → texture/location/cave.tmx
HERO_PATH → texture/hero/
ENEMY_PATH → texture/enemy/
SPIRIT_BOL_PATH → texture/enemy/spirit_bol/
GUN_PATH → texture/gun/
BULLET_PATH → texture/gun/bullet/
```

### Связи уровней

```python
LEVEL_CONNECTIONS = {
    "cave.tmx": {
        "left": {"map": "Library.tmx", "spawn_x": "right_edge"}
    },
    "Library.tmx": {
        "right": {"map": "cave.tmx", "spawn_x": "left_edge"}
    },
}
```

Герой уходит влево в пещере → появляется справа в библиотеке и наоборот.

### Словари анимаций

Три словаря, которые мапят логические имена анимаций на папки с PNG:

- **`HERO_ANIMATIONS`** — 16 ключей: `forward`, `back`, `left`, `right`, `no_move_*`, `with_gun_*`, `with_gun_no_move_*`
- **`ENEMY_ANIMATIONS`** — 12 ключей: `forward`, `back`, `left`, `right`, `no_move_*`, `atack_*`

---

## 🛠️ utils.py — Вспомогательные функции

Три чистые функции без состояния.

### `load_animations(base_path, animation_map)`

Читает папки с PNG и собирает списки файлов.

```
Вход:  base_path = texture/hero/
       animation_map = {"forward": "forward", "back": "back", ...}

Выход: {"forward": ["forward/8.png", "forward/9.png", ...],
        "back": ["back/1.png", "back/2.png", ...], ...}
```

Алгоритм:
1. Для каждого ключа словаря берёт имя папки
2. Ищет все `*.png` в `base_path/папка/`
3. Сортирует по числовому имени файла
4. Фильтрует `document.png`
5. Сохраняет список путей в словарь

### `load_layer_options_from_tmx(map_path)`

Читает TMX-файл и определяет какие слои карты нужно хэшировать для коллизий.

```
Вход: путь к cave.tmx
Выход: {"Flors": {"use_spatial_hash": True},
        "Stop": {"use_spatial_hash": True}}
```

Использует `xml.etree.ElementTree` для парсинга. Только слой `Stop` (стены)
получает `use_spatial_hash: True` — это ускоряет collision detection.

---

## 🔫 bullet.py — Снаряды

Два класса и одна общая функция.

### `_collect_pngs(path: Path) → list[Texture]`

Общая функция для загрузки PNG-последовательностей.
Используется обоими классами пуль.

```python
# Если папки нет → пустой список
# Иначе → сортировка по числу в имени, загрузка через arcade.load_texture
```

### `Bullet(arcade.Sprite)` — пуля героя

**Жизненный цикл:**

```
1. __init__(x, y, direction_x, direction_y)
   ├── center_x/y = позиция героя
   ├── change_x/y = direction * BULLET_SPEED
   ├── lifetime = 0
   └── load_bullet_animation()

2. load_bullet_animation()
   ├── ищет PNG в BULLET_PATH (texture/gun/bullet/)
   ├── если нет — ищет в HERO_PATH/bullet/
   └── если нашёл → self.texture = первый кадр, self.frames = все кадры

3. update(delta_time) — каждый кадр
   ├── center_x/y += change_x/y         # движение
   ├── lifetime += delta_time            # тикает таймер
   ├── update_animation(delta_time)      # смена кадра
   └── если lifetime > 1.2 → remove_from_sprite_lists()

4. update_animation(delta_time)
   └── если есть >1 кадра → переключает каждые 0.08 сек
```

### `EnemyBullet(arcade.Sprite)` — огненный шар призрака

Отличается от Bullet:
- Летит **в точку** где стоял герой (не просто по направлению)
- Вычисляет вектор `(target_x - x, target_y - y)` и нормализует его
- Скорость `ENEMY_BULLET_SPEED = 7`
- Урон `ENEMY_BULLET_DAMAGE = 10` (хранится в `self.damage`)
- Время жизни `ENEMY_BULLET_LIFETIME = 2.0` сек
- Масштаб `scale = 2`

```python
# Вектор цели:
dx = target_x - self.center_x
dy = target_y - self.center_y
dist = sqrt(dx² + dy²)
if dist > 0:
    self.change_x = (dx / dist) * ENEMY_BULLET_SPEED
    self.change_y = (dy / dist) * ENEMY_BULLET_SPEED
```

---

## 🧑 characters.py — Персонажи

Два класса в иерархии: `Cherecters → Enemy`.

### `Cherecters(arcade.Sprite)` — базовый персонаж

#### Конструктор `__init__(self, is_hero=True)`

Инициализирует состояние:

| Поле | Начальное значение | Описание |
|---|---|---|
| `change_x/change_y` | 0 | Вектор движения |
| `facing_direction` | `"forward"` | Куда смотрит |
| `cur_texture` | 0 | Текущий кадр анимации |
| `texture_timer` | 0 | Время до следующего кадра |
| `animations` | `{}` | Словарь: ключ → список путей к PNG |
| `has_gun` | `False` | Есть ли пистолет |
| `health` | 100 | Здоровье |
| `speed` | `MOVEMENT_SPEED` (=5) | Скорость перемещения |
| `is_hero` | `True` | Герой или враг |

Сразу после инициализации вызывает `_setup_animations()`.

#### `_setup_animations()`

Определяет какие анимации загружать:
- Герой → `load_animations(HERO_PATH, HERO_ANIMATIONS)`
- Враг → `load_animations(ENEMY_PATH, ENEMY_ANIMATIONS)`

После загрузки ищет первый доступный кадр для начальной текстуры.

#### `equip_gun()`

Вызывается когда герой наступает на пистолет:
1. `has_gun = True`
2. Перезагружает анимации героя (теперь будут `with_gun_*`)
3. Обновляет текстуру вызовом `_set_texture_for_direction()`

#### `update_animation(delta_time)`

Анимация по таймеру:
```
Каждые 0.15 сек:
1. Спрашивает _get_animation_key() — какой ключ анимации сейчас
2. Узнаёт количество кадров в этой анимации
3. cur_texture = (cur_texture + 1) % frame_count
4. Вызывает _set_texture_for_direction() — применить новый кадр
```

#### `_get_animation_key()`

Логика выбора анимации:

```
Если есть пистолет:
    Если движется → "with_gun_{direction}"
    Если стоит    → "with_gun_no_move_{direction}"
Если нет пистолета:
    → self.facing_direction
```

#### `_set_texture_for_direction()`

Главный метод отрисовки персонажа. Состоит из трёх шагов:

```python
def _set_texture_for_direction(self):
    self._update_facing()       # 1. Повернуть персонажа
    anim_key = self._resolve_anim_key()  # 2. Выбрать анимацию
    self._apply_animation(anim_key)      # 3. Нарисовать кадр
```

#### `_update_facing()`

Обновляет `facing_direction` по направлению движения:

```
Если персонаж движется:
    change_x > 0  → "right"
    change_x < 0  → "left"
    change_y > 0  → "forward"
    иначе         → "back"
Если стоит и текущее направление без "no_move_":
    → "no_move_" + facing_direction
```

#### `_resolve_anim_key()`

Ищет ключ анимации с fallback:

```
Попытка 1: ключ по has_gun + facing_direction
    Если есть в self.animations → вернуть

Попытка 2: базовое направление (без no_move_)
    Если двигался → базовое имя
    Если стоял    → "no_move_" + базовое имя
    Если есть в self.animations → вернуть

Попытка 3: любая доступная анимация
    → первый ключ с непустым списком кадров
```

#### `_apply_animation(anim_key)`

Загружает и применяет PNG-текстуру:

```python
frames = self.animations[anim_key]
frame_path = frames[cur_texture % len(frames)]
image = arcade.load_image(frame_path)
self.texture = arcade.Texture(image)
```

Каждый раз создаётся новый `Texture` — это нормально для спрайтовой графики.

#### `update(delta_time)`

Движение:
```python
self.center_x += self.change_x * self.speed
self.center_y += self.change_y * self.speed
```

Умножает нормализованный вектор `change_x/change_y` на скорость.
(Вектор нормализован — значения от -1 до 1, поэтому скорость
не зависит от диагонального движения.)

---

### `Enemy(Cherecters)` — призрак

Наследует всё от `Cherecters`, добавляет AI и боевую систему.

#### Конструктор

| Поле | Значение | Описание |
|---|---|---|
| `health` | 100 | Здоровье призрака |
| `attack_timer` | 0 | Таймер анимации удара |
| `attack_cooldown` | `ENEMY_ATTACK_COOLDOWN` (1.0) | Перезарядка удара |
| `attack_cooldown_timer` | 0 | Текущий остаток перезарядки |
| `is_attacking` | `False` | В процессе атаки |
| `damage_dealt` | `False` | Уже нанёс урон в этой атаке |
| `speed` | `ENEMY_SPEED` (4) | Скорость призрака |
| `target` | `None` | Ссылка на героя |
| `detect_range` | `ENEMY_DETECT_RANGE` (600) | Радиус видимости |
| `attack_range` | `ENEMY_ATTACK_RANGE` (40) | Дистанция удара |
| `ranged_range` | `ENEMY_RANGED_RANGE` (600) | Дальность стрельбы |
| `ranged_cooldown_timer` | 0 | Перезарядка выстрела |
| `bullet_list` | `None` | Ссылка на список пуль из MyGame |

#### `update(delta_time)` — главный цикл призрака

```python
def update(self, delta_time):
    super().update(delta_time)      # движение (из Cherecters)
    self._update_timers(delta_time)  # таймеры
    self._decide_action()            # AI
```

#### `_update_timers(delta_time)`

Обновляет три таймера:

```
1. attack_timer > 0
   → уменьшить
   → если достиг 0: закончить атаку (_end_attack)

2. attack_cooldown_timer > 0 → уменьшить

3. ranged_cooldown_timer > 0 → уменьшить
```

`_end_attack` сбрасывает `is_attacking`, запускает перезарядку,
возвращает `facing_direction` к базовому направлению и обновляет текстуру.

#### `_decide_action()` — принятие решений

```
Если нет цели / атакует / перезаряжается → выход

Вычислить расстояние до цели (dist):

dist >= detect_range (600)
  → Стоим на месте

dist < attack_range (40)
  → Melee атака (_melee_attack)

dist < ranged_range (600) И остыл выстрел
  → Дальняя атака (_ranged_attack)

иначе
  → Бежим к цели (_chase)
```

#### `_melee_attack(dx, dy)`

```
Остановиться
Определить направление (по большей оси):
  |dx| > |dy| → right/left
  иначе      → forward/back
Запустить start_attack(direction)
```

#### `_ranged_attack()`

```
Остановиться
Выстрелить огненным шаром в target.center_x/y
Поставить перезарядку ranged_cooldown_timer
```

`shoot_at(target_x, target_y)` создаёт `EnemyBullet` и добавляет
в `self.bullet_list` (который указывает на `MyGame.enemy_bullet_list`).

#### `_chase(dx, dy, dist)`

```python
self.change_x = dx / dist  # нормализованный вектор к цели
self.change_y = dy / dist
```

#### `start_attack(direction)`

Запускает анимацию атаки:

```
is_attacking = True
attack_timer = 0.5 сек
facing_direction = "atack_{direction}"
Применить первый кадр атаки
```

#### Переопределённые методы

**`_update_facing()`** — в отличие от героя:
- Обновляет направление только если не атакует
- Использует `abs(change_x) >= abs(change_y)` для выбора оси

**`_resolve_anim_key()`** — без gun-вариантов:
- Сначала пробует `self.facing_direction` напрямую (нужно для `atack_*`)
- Fallback на `no_move_*` или базовое направление

---

## 🖥️ game_window.py — Окно игры

Самый большой модуль. Класс `MyGame(arcade.Window)` управляет всем игровым процессом.

### `__init__` — создание игры

```python
def __init__(self, width, height, title, map_path):
    # Списки спрайтов
    self.bullet_list        # пули героя
    self.enemy_bullet_list  # огненные шары
    self.player_list        # герой
    self.enemies            # призраки

    # Камеры
    self.camera             # игровая камера (движется за героем)
    self.ui_camera          # UI-камера (миникарта, HP — неподвижны)

    # Таймеры
    self.shoot_timer = 0

    # Герой
    self.hero = Cherecters(is_hero=True)

    # Загрузка уровня
    self._setup_level(map_path)
```

### `_setup_level` — загрузка уровня

1. Читает TMX-файл через `load_layer_options_from_tmx` + `arcade.load_tilemap`
2. Создаёт `Scene` из карты (для отрисовки)
3. Извлекает слои:
   - `Stop` → стены для физики
   - `gun` → пистолеты
4. Настраивает `PhysicsEngineSimple` (герой + стены)
5. Сбрасывает `gun_picked_up`
6. Вызывает `_spawn_enemies()`

### `_spawn_enemies()`

Читает `object_lists["enemy"]` из карты.
Для каждого объекта с прямоугольной формой создаёт `Enemy`:
- Позиция — центр прямоугольника
- `target = self.hero`
- `bullet_list = self.enemy_bullet_list`

### `center_camera_to_player()`

Плавно двигает камеру за героем:
```
1. Вычислить отставание камеры от героя (dx, dy)
2. Если отставание > мёртвой зоны — двигать камеру
3. Ограничить краями карты
4. Применить CAMERA_SMOOTH для плавности
```

### `shoot()` — выстрел героя

```
1. Проверить: есть ли пистолет, не на перезарядке?
2. Определить направление по facing_direction
3. Создать Bullet(hero.x, hero.y, dx, dy)
4. Добавить в bullet_list
5. Поставить shoot_timer = SHOOT_DELAY
```

### `on_update(delta_time)` — игровой цикл (60 FPS)

Читается сверху вниз:

```python
def on_update(self, delta_time):
    self._update_timers(delta_time)        # таймер выстрела
    self.physics_engine.update()           # физика (стены)
    self._try_pickup_gun()                 # подбор пистолета
    self._update_bullets(delta_time)       # пули героя → стены/враги
    self._update_hero(delta_time)          # анимация + движение героя
    self._update_enemy_bullets(delta_time) # шары призрака → стены/герой
    self._update_enemies(delta_time)       # AI + анимация врагов
    if self.hero.health <= 0:             # смерть
        self.close()
        return
    self._check_level_transition()         # переход между уровнями
    self.center_camera_to_player()         # камера
```

Каждый под-метод делает одну операцию:

**`_update_timers`** — уменьшает `shoot_timer` на `delta_time`

**`_try_pickup_gun`** — проверяет коллизию героя с каждым `gun` спрайтом.
Если есть пересечение — удаляет пистолет со сцены и вызывает `hero.equip_gun()`.

**`_update_bullets`** — двигает каждую пулю. Проверяет:
- Collision со стеной → удалить пулю
- Collision с врагом → удалить пулю, отнять 25 HP у врага

**`_update_hero`** — `hero.update_animation(delta_time)` + `hero.update(delta_time)`

**`_update_enemy_bullets`** — двигает каждый шар. Проверяет:
- Collision со стеной → удалить
- Collision с героем → отнять `bullet.damage` HP, удалить шар

**`_update_enemies`** — для каждого врага:
- `enemy.update(delta_time)` — AI + движение
- `enemy.update_animation(delta_time)` — анимация
- Проверка melee-атаки: если враг атакует, не нанёс ли урон,
  и есть коллизия с героем → отнять `ENEMY_DAMAGE` HP

### `_draw_hp()` — полоска здоровья

Рисуется в правом верхнем углу (на `ui_camera`):

```
Фон: серый прямоугольник 200x20px
Заливка: зелёный (>60%) / жёлтый (30-60%) / красный (<30%)
Рамка: белая
Текст: "HP: {число}"
```

### `_draw_minimap()` — миникарта

Рисуется в левом верхнем углу:

```
150x100px, полупрозрачный чёрный фон
Серые квадраты — стены
Жёлтые точки — пистолеты (если не подобраны)
Красные точки — призраки
Зелёная точка — герой
```

Масштаб вычисляется динамически:
```python
scale_x = minimap_width / map_pixel_width
scale_y = minimap_height / map_pixel_height
```

### `_check_level_transition()` — переход между уровнями

Проверяет не вышел ли герой за край карты:

```
center_x < 0               → left
center_x > map_pixel_width → right
center_y < 0               → down
center_y > map_pixel_height → up

Если для текущей карты есть переход в этом направлении:
  1. Загрузить новую карту (_load_map)
  2. Установить позицию героя:
     left_edge → x = 100
     right_edge → x = map_pixel_width - 100
     иначе → центр карты
```

### Управление (`on_key_press`, `on_key_release`)

```python
W/A/S/D    → change_x/change_y = ±1 (нормализованный вектор)
Пробел     → shoot() (если есть пистолет и прошла перезарядка)
Отпускание → change_x/change_y = 0
```

Каждое нажатие/отпускание также вызывает `_set_texture_for_direction()` —
чтобы персонаж сразу повернулся в нужную сторону.

### `on_draw()` — отрисовка

```
1. Очистить экран
2. Активировать игровую камеру
3. Нарисовать все слои сцены, кроме "gun"
4. Нарисовать пистолеты (отдельно, если не подобраны)
5. Нарисовать героя, пули, шары, врагов
6. Активировать UI-камеру
7. Нарисовать миникарту
8. Нарисовать полоску HP
```

Слой "gun" рисуется отдельно от сцены, чтобы контролировать
его видимость в зависимости от `has_gun` и `gun_picked_up`.

---

## 🔄 Игровой цикл (полная трассировка)

```
1. Запуск main() → создание MyGame(cave.tmx)
2. _setup_level("cave.tmx")
   ├── загрузка карты
   ├── поиск стен, пистолетов
   └── спавн врагов (в пещере нет)
3. on_show() → герой в центре карты

=== ИГРОВОЙ ЦИКЛ (60 раз/сек) ===

4. Игрок нажимает WASD
5. on_key_press → change_x/y = ±1, обновление текстуры
6. on_update:
   a. Физика — герой не проходит сквозь стены
   b. Если наступил на пистолет → equip_gun(), has_gun = True
   c. Пули героя двигаются, проверяют коллизии
   d. Герой двигается и анимируется
   e. Пули врага двигаются, проверяют коллизии
   f. Враги принимают решения (бежать/атаковать/стрелять)
   g. Если герой умер → game over
   h. Если герой ушёл за край → загрузка новой карты
   i. Камера двигается за героем
7. on_draw:
   a. Отрисовка карты
   b. Отрисовка спрайтов
   c. Отрисовка UI

=== ПЕРЕХОД НА ДРУГОЙ УРОВЕНЬ ===

8. Герой уходит за левый край пещеры
9. _check_level_transition → _load_map("Library.tmx")
10. _setup_level("Library.tmx") — загрузка библиотеки
11. Герой появляется справа (x = map_pixel_width - 100)
12. В библиотеке есть призрак:
    - Бежит за героем
    - Если близко → бьёт
    - Если далеко → стреляет огненными шарами
    - Герой может стрелять в ответ
13. Если герой уходит за правый край → возврат в пещеру

=== СМЕРТЬ ===

14. health <= 0 → self.close() → игра закрывается
```

---

## 🎮 Управление

| Клавиша | Действие |
|---|---|
| W | Вверх |
| A | Влево |
| S | Вниз |
| D | Вправо |
| Пробел | Стрелять (нужен пистолет) |

---

## 🧱 Формат карт (Tiled)

Карты созданы в редакторе **Tiled** и сохранены в формате `.tmx`.

### Слои

| Слой | Тип | Назначение |
|---|---|---|
| `Flors` | Tile layer | Пол, декор |
| `Stop` | Tile layer | Стены (physics collision) |
| `gun` | Tile layer | Спавн пистолета (только cave.tmx) |
| `enemy` | Object layer | Спавн призраков (только Library.tmx) |

### Система координат

Tiled использует Y↑ (стандартная декартова система, как в Arcade).
Карты 60×40 тайлов, каждый 32×32 пикселя → 1920×1280 px.

### Tileset reference

| TSX | GID range | Tile count | Источник |
|---|---|---|---|
| `stone.tsx` | 1–4 | 4 | `Tail/cave.png/0.png` |
| `ditch.tsx` | 5–260 | 256 | `Tail/ditch.png` |
| `gun.tsx` | 261–276 | 16 | `Tail/gun.png` |
| `wood.tsx` | 277–280 | 4 | `Tail/library.png/0.png` |
