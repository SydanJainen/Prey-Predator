from dataclasses import dataclass, field
from math import floor
import random
import uuid
from genome import Genome

@dataclass
class Prey:
    
    x : int 
    y : int
    genome : Genome = field(default_factory=Genome) 
    food_eated : int = 0
    time_spawn : int = 0
    time_alive : int = 0
    id : uuid = field(default_factory=uuid.uuid4)
    food_weight = 10

    def __post_init__(self):
        self.fitness : list = [0]
        self.current_energy : list =[self.genome.starting_energy]
        self.time_alive = 0
        self.id = uuid.uuid4()

    def action(self, ambient):
        #if there is 1 or more predator in vision range, run away
        if ambient.get_number_of_predator_in_range(self.x, self.y, self.genome.vision) > 1:
            #print("run away")
            self.run_away(ambient)
            self.genome.voracity += 1
        else:
            #if there is 1 or more food in vision range, move towards it
            num_food = ambient.get_number_of_food_in_range(self.x, self.y, self.genome.vision)
            if  num_food > 0:
                self.move_towards_food(ambient)
            else:
                #if there is no food in vision range, move randomly
                #print("move_randomly")
                self.move_randomly(ambient)
                self.genome.voracity += 1
        self.update_energy()
        self.time_alive += 1

    def update_energy(self):
        tmp : int = self.get_current_energy() - self.energy_cost() 
        if tmp <= 0:
            self.current_energy.append(0)
        else:
            self.current_energy.append(tmp)

    def energy_cost(self) -> int:
        if ( self.time_alive > 6):
            return floor(self.get_voracity() + self.get_dimension() + (10*self.time_alive))
        else:
            return floor(self.get_voracity() + self.get_dimension() )

    def run_away(self, ambient):
        #get the predators in vision range
        predators_in_range = ambient.get_predators_in_range(self.x, self.y, self.genome.vision)
        #get the closest predator
        closest_predator = min(predators_in_range, key=lambda x: abs(x.x - self.x) + abs(x.y - self.y))
        #get the direction of the closest predator
        direction = self.get_direction(closest_predator)
        #move the prey in the direction of the closest predator
        ambient.move(self.x, self.y, self.x - direction[0], self.y - direction[1])

    def move_randomly(self, ambient):
        #get a random direction
        direction = self.get_random_direction()
        #move the prey in the direction
        if ambient.is_empty(self.x + direction[0], self.y + direction[1]):
            ambient.move(self.x, self.y, self.x + direction[0], self.y + direction[1])

    def get_random_direction(self):
        #return a random direction
        return [self.get_random_number(-1, 1), self.get_random_number(-1, 1)]

    def get_random_number(self, min, max):
        #return a random number between min and max
        return random.randint(min, max)

    def move_towards_food(self, ambient):
        food_in_range = ambient.get_food_in_range(self.x, self.y, self.genome.vision)
        if len(food_in_range) > 0:
            #get the closest food
            closest_food = min(food_in_range, key=lambda x: abs(x.x - self.x) + abs(x.y - self.y))
            # if speed is greater than the distance between the prey and the closest food, the prey will move towards the closest food
            if self.get_speed() > abs(closest_food.x - self.x) + abs(closest_food.y - self.y):
                ambient.remove_object(closest_food.x, closest_food.y)
                ambient.move(self.x, self.y,closest_food.x, closest_food.y)
                self.food_eated += 1
                new_energy = self.get_current_energy() + (self.get_starting_energy()//2) if (self.get_current_energy() + (self.get_starting_energy()//2) < self.get_starting_energy()) else self.get_starting_energy()
                self.current_energy.append(new_energy)
                self.genome.voracity = self.genome.voracity - self.food_weight*(self.time_alive // 2) if self.genome.voracity >  self.food_weight*(self.time_alive // 2) else 0
                #print("food_eated")          
            # if speed is less than the distance between the prey and the closest food, the prey will move towards the closest food
            else:
                #get the direction of the closest food
                direction = self.get_direction(closest_food)
                #move the prey in the direction of the closest food
                ambient.move( self.x, self.y, self.x + direction[0], self.y + direction[1])
                self.genome.voracity += 1
        #else:
            #print("no food in range")

    def get_direction(self, closest_food):
        #return the direction of the closest food
        return [closest_food.x - self.x, closest_food.y - self.y]

    def get_fitness(self):
        #return the last element of the fitness list
        return self.fitness[-1]

    def update_fitness(self, actual_generation):
        # the preys with a big amount of energy over the time will have a good fitness.
        # energy variation divided by time will be the fitness * the maximun energy
        try:
            self.fitness.append((self.food_eated *self.food_weight) +(self.current_energy[-1] / self.time_alive))
        except ZeroDivisionError:
            self.fitness.append(0)
        #check function

    def chance_of_life(self, ambient):
        #number of predators in vision range divided by the number of predators in max vision range
        return ambient.get_number_of_predator_in_range(self.x, self.y, self.genome.vision) / ambient.get_number_of_predator_in_range(self.x, self.y, self.genome.get_max_vision())

    def get_voracity(self):
        #return the voracity of the prey
        return self.genome.voracity

    def get_max_vision(self):
        #return the max vision of the prey
        return self.genome.get_max_vision()

    def get_speed(self):
        #return the speed of the prey
        return self.genome.speed
    
    def get_vision(self):
        #return the vision of the prey
        return self.genome.vision
    
    def get_dimension(self):
        #return the dimension of the prey
        return self.genome.dimension
    
    def get_starting_energy(self):
        #return the starting energy of the prey
        return self.genome.starting_energy

    def get_current_energy(self):
        #return the current energy of the prey
        return self.current_energy[-1]

    def has_eaten(self) -> bool:
        #return true if the prey has eaten
        return self.food_eated > 0

    def get_genome(self):
        #return the genome of the prey
        return self.genome

    def get_time_spawn(self):
        #return the time spawn of the prey
        return self.time_spawn

    def get_time_alive(self):
        #return the time alive of the prey
        return self.time_alive

    def get_food_eated(self):
        #return the food eated of the prey
        return self.food_eated

    def to_json(self):
        #return a json object with the genome of the prey
        return {
                "x": self.x,
                "y": self.y,
                "genome": self.genome.to_json(),
                "time_spawn": self.time_spawn,
                "time_alive": self.time_alive,
                "food_eated": self.food_eated,
                "fitness": self.fitness,
                "current_energy": self.current_energy,
                "id": str(self.id)
            }
        