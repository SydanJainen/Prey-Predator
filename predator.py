from dataclasses import dataclass, field
from math import floor
import random
import uuid
from genome import Genome

@dataclass
class Predator:

    x : int
    y : int  
    
    genome : Genome = field(default_factory=Genome) 
    food_eated : int = 0
    time_spawn : int = 0
    time_alive : int = 0
    id : uuid = field(default_factory=uuid.uuid4)
    energy_factor = 10
    
    def __post_init__(self):
        self.fitness : list = [0]
        self.current_energy : list =[self.genome.starting_energy]
        self.time_alive = 0
        self.id = uuid.uuid4()
        assert( self.time_alive == 0)

    def action(self, ambient):
        dict_of_prey = ambient.get_dict_of_prey(self.x, self.y, self.get_vision())
        if len(dict_of_prey) > 0:
            #print("predator_hunt")
            self.hunt(ambient, dict_of_prey)
        else:
            self.move_randomly(ambient)
            self.genome.voracity += 1
        self.update_energy()
        self.time_alive += 1

    def hunt(self, ambient, dict_of_prey):
        #get the closest prey
        closest_prey = self.get_closest_prey(dict_of_prey)
        #get the direction of the closest prey
        direction = self.get_direction(closest_prey)
        #move the predator in the direction of the closest prey

        if self.get_speed() > abs(closest_prey.x - self.x) + abs(closest_prey.y - self.y):
            if ( (self.genome.dimension * self.genome.voracity//5 ) + self.genome.damage >= closest_prey.get_dimension()):
                self.eat(ambient, closest_prey)
            else:
                self.current_energy[-1] -= closest_prey.genome.damage if self.current_energy[-1] > closest_prey.genome.damage else 0
                closest_prey.current_energy[-1] -= self.genome.damage if closest_prey.current_energy[-1] > self.genome.damage else 0
                if closest_prey.current_energy[-1] == 0:
                    self.eat(ambient, closest_prey)
                else:
                    closest_prey.genome.dimension -= self.genome.damage
                    if closest_prey.genome.dimension < 0:
                        self.eat(ambient, closest_prey)
                    else:
                        self.genome.voracity += 1 
        else:
            ambient.move(self.x, self.y, self.x + direction[0], self.y + direction[1])
            self.genome.voracity += 1 

    def eat(self, ambient, closest_prey):
        ambient.remove_object(closest_prey.x, closest_prey.y)
        ambient.move(self.x, self.y,closest_prey.x, closest_prey.y)
        self.food_eated += 1
        new_energy = self.get_current_energy() + (self.get_starting_energy()//2) if (self.get_current_energy() + (self.get_starting_energy()//2) < self.get_starting_energy()) else self.get_starting_energy()
        self.current_energy.append(new_energy)
        self.genome.voracity = self.genome.voracity - self.time_alive if self.genome.voracity >  self.time_alive  else 0

    def get_closest_prey(self, dict_of_prey: dict):
        prey = None
        for key in dict_of_prey.keys():
            i, j = key
            distance = self.get_distance(i, j)
            if prey == None or distance < prey[1]:
                prey = [dict_of_prey.get(key), distance]
        return prey[0]

    def get_distance(self, x, y):
        #return the distance between the predator and the prey
        return (x - self.x) ** 2 + (y - self.y) ** 2

    def update_energy(self):
        tmp : int = self.get_current_energy() - self.energy_cost() 
        if tmp <= 0:
            self.current_energy.append(0)
        else:
            self.current_energy.append(tmp)

    def energy_cost(self) -> int:
        return floor(self.get_voracity() + self.get_dimension() + (self.energy_factor * self.time_alive) )

    def move_randomly(self, ambient):
        #get a random direction
        direction = self.get_random_direction()
        #move the predator in the direction
        if ambient.is_empty(self.x + direction[0], self.y + direction[1]):
            ambient.move(self.x, self.y, self.x + direction[0], self.y + direction[1])

    def get_random_direction(self):
        #return a random direction
        return [self.get_random_number(-1, 1), self.get_random_number(-1, 1)]

    def get_random_number(self, min, max):
        #return a random number between min and max
        return random.randint(min, max)

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
            self.fitness.append((self.food_eated * self.energy_factor) +(self.current_energy[-1] / self.time_alive))
        except ZeroDivisionError:
            self.fitness.append(0)
        #check function

    def chance_of_life(self, ambient):
        #number of predators in vision range divided by the number of predators in max vision range
        return ambient.get_number_of_predator_in_range(self.x, self.y, self.get_vision()) / ambient.get_number_of_predator_in_range(self.x, self.y, self.genome.get_max_vision())

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
    
    def get_food_eated(self):
        #return the food eated of the prey
        return self.food_eated
        
    def has_eaten(self) -> bool:
        #return true if the prey has eaten
        return self.food_eated > 0

    def chance_to_hunt(self, ambient):
       return ambient.get_number_of_prey_in_range(self.x, self.y, self.get_vision()) / ambient.get_number_of_prey_in_range(self.x, self.y, self.genome.get_max_vision())

    def get_genome(self):
        #return the genome of the prey
        return self.genome

    def get_time_alive(self):
        #return the time alive of the prey
        return self.time_alive

    def get_time_spawn(self):
        #return the time spawn of the prey
        return self.time_spawn

    def to_json(self):
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