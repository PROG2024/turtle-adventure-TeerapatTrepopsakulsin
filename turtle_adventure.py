"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
import time
import random
from math import cos, sin, atan2, exp, log, fabs
from turtle import RawTurtle
from gamelib import Game, GameElement



def exclude(list_all, list_exclude_item):
    return [item for item in list_all if item not in list_exclude_item]


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color
        self.__start_time = time.time()

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    @property
    def start_time(self) -> float:
        """
        Get the color of the enemy
        """
        return self.__start_time

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.x += 1
        self.y += 1
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class StalkEnemy(Enemy):
    """
    Stalking enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 level=1):
        super().__init__(game, size, color)
        self.__id = None
        self.level = level
        self.speed = (1 - exp(-self.level)) * self.level * 0.02 + 0.5

    def create(self) -> None:
        self.x = random.choice(exclude(list(range(0, self.game.canvas.winfo_width())),
                                       list(range(int(self.game.player.x - 20), int(self.game.player.x + 20)))))
        self.y = random.choice(exclude(list(range(0, self.game.canvas.winfo_height())),
                                       list(range(int(self.game.player.y - 20), int(self.game.player.y + 20)))))
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        angle = atan2((self.game.player.y - self.y), (self.game.player.x - self.x))
        self.x += cos(angle) * 2 * self.speed
        self.y += sin(angle) * self.speed
        if self.hits_player():
            self.game.game_over_lose()
        self.delete()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        if time.time() - self.start_time >= 3000*int(log(self.level + 1)):
            self.x, self.y = -999, -999
            self.canvas.delete(self.__id)


class FencingEnemy(Enemy):
    """
    Fencing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 level=1):
        super().__init__(game, size, color)
        self.__id = None
        self.level = level
        self.speed = log(self.level + 1, 20) * self.level * 0.05 + 0.7
        self.fence = random.choice(list(range(20, 50)))
        self.__movement = self.up

    @property
    def movement(self):
        return self.__movement

    @movement.setter
    def movement(self, value):
        self.__movement = value

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)
        self.x = self.game.home.x + self.fence
        self.y = self.game.home.y + self.fence

    def update(self) -> None:
        self.movement()
        if self.hits_player():
            self.game.game_over_lose()
        self.delete()

    def up(self):
        self.y -= self.speed
        if self.y <= self.game.home.y - self.fence:
            self.movement = self.left

    def down(self):
        self.y += self.speed
        if self.y >= self.game.home.y + self.fence:
            self.movement = self.right

    def left(self):
        self.x -= self.speed
        if self.x <= self.game.home.x - self.fence:
            self.movement = self.down

    def right(self):
        self.x += self.speed
        if self.x >= self.game.home.x + self.fence:
            self.movement = self.up

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        if time.time() - self.start_time >= 30:
            self.x, self.y = -999, -999
            self.canvas.delete(self.__id)


class RandomWalkEnemy(Enemy):
    """
    Random walk Enemy
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 level=1):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 7 * log(level, 50) + 3.7
        self.direction = random.choice(list(range(360)))

        self.x_movement = random.choice((self.left, self.right))
        self.y_movement = random.choice((self.up, self.down))

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)
        self.x = random.choice(exclude(list(range(0, self.game.canvas.winfo_width())),
                                       list(range(int(self.game.player.x - 20), int(self.game.player.x + 20)))))
        self.y = random.choice(exclude(list(range(0, self.game.canvas.winfo_height())),
                                       list(range(int(self.game.player.y - 20), int(self.game.player.y + 20)))))

    def update(self) -> None:
        self.x_movement()
        self.y_movement()
        if self.hits_player():
            self.game.game_over_lose()
        self.delete()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def up(self):
        self.y -= fabs(sin(self.direction)) * self.speed
        if self.y <= 0:
            self.y_movement = self.down

    def down(self):
        self.y += fabs(sin(self.direction)) * self.speed
        if self.y > self.game.screen_height:
            self.y_movement = self.up

    def left(self):
        self.x -= fabs(cos(self.direction)) * self.speed
        if self.x <= 0:
            self.x_movement = self.right

    def right(self):
        self.x += fabs(cos(self.direction)) * self.speed
        if self.x > self.game.canvas.winfo_width():
            self.x_movement = self.left

    def delete(self) -> None:
        if time.time() - self.start_time >= 5:
            self.x, self.y = -999, -999
            self.canvas.delete(self.__id)


class StraightEnemy(Enemy):
    """
    Straight Enemy
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 direction=0,
                 level=1):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = 7 * log(level, 49)
        self.__direction = direction

    @property
    def direction(self):
        return self.__direction

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)
        self.x = random.choice(exclude(list(range(0, self.game.canvas.winfo_width())),
                                       list(range(int(self.game.player.x - 20), int(self.game.player.x + 20)))))
        self.y = random.choice(exclude(list(range(0, self.game.canvas.winfo_height())),
                                       list(range(int(self.game.player.y - 20), int(self.game.player.y + 20)))))

    def update(self) -> None:
        self.x += cos(self.direction) * self.speed
        self.y += sin(self.direction) * self.speed
        if self.hits_player():
            self.game.game_over_lose()
        self.delete()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        if (self.x > self.canvas.winfo_width() or
                self.x < 0 or
                self.y > self.canvas.winfo_height() or
                self.y < 0):
            self.canvas.delete(self.__id)


class LaserEnemy(Enemy):
    """
    Laser Enemy
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 delay=0.0,
                 level=1):
        super().__init__(game, size, color)
        self.__id = None
        self.level = level
        self.speed = 10*(1/(1.01**self.level))/11
        self.__direction = None
        self.state = self.inactive
        self.delay = delay

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, value):
        self.__direction = value

    def create(self) -> None:
        x0 = random.choice(list(range(-self.game.canvas.winfo_width(), 2*self.game.canvas.winfo_width())))
        x1 = random.choice(list(range(-self.game.canvas.winfo_width(), 2*self.game.canvas.winfo_width())))
        y0 = -1
        y1 = self.game.canvas.winfo_height() + 1

        self.__id = self.canvas.create_line(x0, y0, x1, y1, fill="gray", width=3)
        self.x, self.y = x0, y0
        self.direction = atan2(y1-y0, x1-x0)

    def inactive(self):
        if time.time() - self.start_time >= self.speed + self.delay:
            self.state = self.active

    def active(self):
        self.canvas.itemconfigure(self.__id, fill=self.color)
        if self.hits_line():
            self.game.game_over_lose()
        self.delete()

    def hits_line(self):
        cur_direction = atan2(self.game.player.y-self.y, self.game.player.x-self.x)
        return fabs(cur_direction - self.direction) <= 0.01

    def update(self) -> None:
        self.state()

    def render(self) -> None:
        pass

    def delete(self) -> None:
        if time.time() - self.start_time >= 2 * self.speed + self.delay:
            self.direction = -999
            self.canvas.delete(self.__id)


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAdvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    @level.setter
    def level(self, value):
        self.__level = value

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        if self.level % 2 == 0:
            stalk_enemy = StalkEnemy(self.__game, 7, "magenta", level=self.level)
            self.game.add_element(stalk_enemy)

        if self.level % 7 == 0:
            fencing_enemy = FencingEnemy(self.__game, 10, "red", level=self.level)
            self.game.add_element(fencing_enemy)

        random_walk_enemy = RandomWalkEnemy(self.__game, 14, "blue", level=self.level)
        self.game.add_element(random_walk_enemy)

        if self.level % 3 == 0:
            random_angle = random.choice(list(range(360)))
            straight_enemy = StraightEnemy(self.__game, 37, "yellow", level=self.level, direction=random_angle)
            self.game.add_element(straight_enemy)

        k = 5
        if self.level % 10 == 0:
            k = 3
        laser_num = int(log(self.level, 15) * self.level) // k
        for i in range(laser_num):
            laser_enemy = LaserEnemy(self.__game, 14, "black", level=self.level, delay=0.02*i)
            self.game.add_element(laser_enemy)

        spd = 10*(1/(1.01**self.level))/11
        round_duration = laser_num*20 + int(1000 * 2 * spd)
        self.game.canvas.itemconfigure(self.game.level_text, text=f"Level: {self.level}")
        self.level += 1
        if self.game.is_started:
            self.game.after(round_duration, lambda: self.create_enemy())


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

        font = ("Arial", 7, "bold")
        self.level_text = self.canvas.create_text(20,
                                5,
                                text=f"Level : {self.level}",
                                font=font,
                                fill="red")

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
