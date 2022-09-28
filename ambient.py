#define a n X m ambient. in each tiles there is a probability of spawning a food if the tile is empty
from dataclasses import dataclass
import json
from food import Food
from predator import Predator
from prey import Prey

@dataclass
class Ambient:
    width : int
    height : int

    def __post_init__(self):
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

    def set_grid(self, x, y, obj) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        if self.grid[x][y] is not None:
            return False
        self.grid[x][y] = obj
        return True

    def get_grid(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        if self.grid[x][y] is None:
            return None
        return self.grid[x][y]

    def remove_object(self, x, y):
        self.grid[x][y] = None

    def get_food_in_range(self, x:int, y:int, vision:int) -> list:
        foods = []
        coor_x_min = x - vision if x - vision >= 0 else 0
        coor_y_min = y - vision if y - vision >= 0 else 0
        coor_x_max = x + vision if x + vision  < self.width else self.width -1
        coor_y_max = y + vision if y + vision  < self.height else self.height -1
        for i in range(coor_x_min, coor_x_max):
            for j in range(coor_y_min, coor_y_max):
                obj = self.get_grid(i, j)
                #print(obj)
                if obj != None :
                    if isinstance(obj, Food):
                        #print("food found")
                        foods.append(obj)
        return foods

    def get_number_of_food_in_range(self, x:int, y:int, vision:int ) -> int:
        number_of_food = 0
        coor_x_min = x - vision if x - vision >= 0 else 0
        coor_y_min = y - vision if y - vision >= 0 else 0
        coor_x_max = x + vision if x + vision  < self.width else self.width -1
        coor_y_max = y + vision if y + vision  < self.height else self.height -1
        for i in range(coor_x_min, coor_x_max):
            for j in range(coor_y_min, coor_y_max):
                obj = self.get_grid(i, j)
                if obj != None :
                    if isinstance(obj, Food):
                        #print("incrementing number of food", i, j)
                        number_of_food += 1
        return number_of_food
    
    def move(self, x, y, new_x, new_y):
        if self.get_grid(new_x, new_y) is not None:
            return False
        if new_x < 0:
            new_x = 0
        if new_x >= self.width:
            new_x = self.width - 1
        if new_y < 0:
            new_y = 0
        if new_y >= self.height:
            new_y = self.height - 1
        if self.grid[x][y] is not None:
            creature = self.grid[x][y]
            # if creature has attributes x and y then
            if hasattr(creature, 'x') and hasattr(creature, 'y'):
                creature.x = new_x
                creature.y = new_y
            self.grid[new_x][new_y] = creature
            self.grid[x][y] = None
            return True
        return False

    def get_list_of_empty(self) -> list:
        tmp = [] 
        for i in range(self.height):
            for j in range(self.width):
                if  self.grid[i][j] is None:
                    tmp.append((i,j))
        return tmp

    def get_number_of_empty_in_range(self, x:int, y:int, vision:int ) -> int:
        number_of_empty = 0
        coor_x_min = x - vision if x - vision >= 0 else 0
        coor_y_min = y - vision if y - vision >= 0 else 0
        coor_x_max = x + vision + 1 if x + vision + 1 < self.width else self.width
        coor_y_max = y + vision + 1 if y + vision + 1 < self.height else self.height
        for i in range(coor_x_min, coor_x_max):
            for j in range(coor_y_min, coor_y_max):
                if self.get_grid(i, j) is None:
                    number_of_empty += 1
        return number_of_empty

    def get_dict_of_prey(self,x,y,vision) -> dict:
        coor_x_min = x - vision if x - vision >= 0 else 0
        coor_y_min = y - vision if y - vision >= 0 else 0
        coor_x_max = x + vision + 1 if x + vision + 1 < self.width else self.width
        coor_y_max = y + vision + 1 if y + vision + 1 < self.height else self.height
        return {(i,j):self.get_grid(i,j) for i in range(coor_x_min, coor_x_max) for j in range(coor_y_min, coor_y_max) if self.get_grid(i,j) is not None and isinstance(self.get_grid(i,j),Prey)}
        

    def get_number_of_prey_in_range(self, x, y, vision) -> int:
        number_of_prey = 0
        coor_x_min = x - vision if x - vision >= 0 else 0
        coor_y_max = y - vision if y - vision >= 0 else 0
        coor_x_max = x + vision + 1 if x + vision + 1 < self.width else self.width
        coor_y_min = y + vision + 1 if y + vision + 1 < self.height else self.height
        for i in range(coor_x_min, coor_x_max):
            for j in range(coor_y_min, coor_y_max):
                if self.get_grid(i, j) is not None and isinstance(self.get_grid(i, j), Prey):
                    number_of_prey += 1
        return number_of_prey

    def get_number_of_predator_in_range(self, x, y, vision) -> int:
        number_of_predator = 0
        coor_x_min = x - vision if x - vision >= 0 else 0
        coor_y_max = y - vision if y - vision >= 0 else 0
        coor_x_max = x + vision + 1 if x + vision + 1 < self.width else self.width
        coor_y_min = y + vision + 1 if y + vision + 1 < self.height else self.height
        for i in range(coor_x_min, coor_x_max):
            for j in range(coor_y_min, coor_y_max):
                if self.get_grid(i, j) is not None and isinstance(self.get_grid(i, j), Predator):
                    number_of_predator += 1
        return number_of_predator 

    def get_preys(self) -> list:
        return [ self.grid[x][y] for x in range(self.width) for y in range(self.height) if isinstance(self.grid[x][y], Prey)]

    def get_predators(self) -> list:
        return [ self.grid[x][y] for x in range(self.width) for y in range(self.height) if isinstance(self.grid[x][y], Predator)]

    def get_foods(self) -> list:
        return [ self.grid[x][y] for x in range(self.width) for y in range(self.height) if isinstance(self.grid[x][y], Food)]

    def get_grid_of_string(self) -> str:
        grid_string = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] is None:
                    grid_string += " . "
                elif isinstance(self.grid[i][j], Prey):
                    grid_string += " P "
                elif isinstance(self.grid[i][j], Predator):
                    grid_string += " D "
                elif isinstance(self.grid[i][j], Food):
                    grid_string += " F "
            grid_string += "\n"
        return grid_string

    def is_empty(self, x, y) -> bool:
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        return self.grid[x][y] is None

    def get_stats_grid(self, division):
        #divide the height and width of the grid by the division
        #return a list of list of tuple (number of preys, number of predators, number of food)
        height_step = self.height // division
        width_step = self.width // division
        total_stats = {}
        #calculate the number of preys, predators and food in each square of the grid calculated by the division
        for i in range(division):
            for j in range(division):
                stats = {
                    "preys": 0,
                    "predators": 0,
                    "food": 0
                }
                for x in range(i*height_step, (i+1)*height_step):
                    for y in range(j*width_step, (j+1)*width_step):
                        if isinstance(self.grid[x][y], Prey):
                            stats["preys"] += 1
                        elif isinstance(self.grid[x][y], Predator):
                            stats["predators"] += 1
                        elif isinstance(self.grid[x][y], Food):
                            stats["food"] += 1
                total_stats.update({(i,j):stats})
        return total_stats
        

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
