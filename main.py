#define a class that coordinate a genetic algorithm
from dataclasses import dataclass
from math import floor
import os
from random import random, randint
import time
from ambient import Ambient
import json
from food import Food
from genome import Genome
from predator import Predator
from prey import Prey
import matplotlib as mpl
from matplotlib import pyplot as plt
import sys

with open('configuration/config.json') as param_file:
    param = json.load(param_file)

    WIDTH = param["game"]['width']
    HEIGHT = param["game"]['height']
    ACTIONS_IN_GENERATION = param["hp_ga"]['actions_in_generation']
    MAX_GENERATION = param["hp_ga"]['max_generations']
    PREY_INITIAL_POPULATION = param["hp_ga"]['prey_initial_population']
    PREDATOR_INITIAL_POPULATION = param["hp_ga"]['predator_initial_population']
    FOOD = param["hp_ga"]['max_food']
    SPAWN_FOOD = param["hp_ga"]['spawn_food']
    PREY_BIRTHRATE = param["prey"]['birthrate']
    PREDATOR_BIRTHRATE = param["predator"]['birthrate']

    param_file.close()

@dataclass
class GeneticAlgotithm:
    is_simulation_ended = False
     
    """
    post_init

    Arguments:
        is_simulation_ended {bool} -- Default False. If True the simulation is ended
    Returns:
        None
    """    
    def __post_init__(self):
        self.actual_generation = 1
        #define ambient
        self.ambient = Ambient(WIDTH, HEIGHT)
        self.log_folder = "./log/" + str(int(time.time()))
        os.mkdir(self.log_folder)
        with open(self.log_folder + "/log.json", 'w') as f:
            json.dump(param, f)
        #-------------START ----------------------
        for _ in range(PREY_INITIAL_POPULATION):
            self.spawn_object("Prey")
        for _ in range(PREDATOR_INITIAL_POPULATION):
            self.spawn_object("Predator")
        for _ in range(FOOD):
            self.spawn_object("Food")
        #save json with the initial configuration of the simulation
        self.save_json()
        print("Simulation started")        
        #print(self.ambient.get_grid_of_string())
        self.run()

    """
    spawn_object
    Arguments:
        obj {str} -- string is Prey, Predator or Food and define the object to spawn.
    Returns:
        None
    """    
    def spawn_object(self, obj: str):
        empty_list = self.ambient.get_list_of_empty()
        if  len(empty_list) == 0 :
            return
        random_index = randint(0, len(empty_list) - 1)
        x,y = empty_list[random_index]
        if obj == "Prey":
            self.ambient.set_grid(x, y, Prey(x,y,time_spawn=self.actual_generation))
        if obj == "Predator":
            self.ambient.set_grid(x, y, Predator(x,y,time_spawn=self.actual_generation))
        if obj == "Food":
            self.ambient.set_grid(x, y, Food(x,y,time_spawn=self.actual_generation))

    """
    spawn_food
    Arguments:
        food {int} -- number of food to spawn
    Returns:
        None
    """    
    def spawn_food(self, food=SPAWN_FOOD):
        for _ in range(food):
            if (len(self.ambient.get_foods()) > ((WIDTH*HEIGHT)//3)):
                break
            else:
                self.spawn_object("Food")

    """
    remove_dead_objects
    Arguments:
        obj {Prey or Predator} -- object to remove
    Returns:
        None
    """    
    def remove_dead_objects(self, obj: Prey or Predator):
        self.ambient.remove_object(obj.x, obj.y)
        del obj

    def run(self):
        for _ in range(MAX_GENERATION):
            if self.is_simulation_ended:
                break
            self.run_generation()
            self.evaluate_fitness()
            self.check_if_simulation_ended()
            self.evolution_step()
            self.spawn_food(SPAWN_FOOD)
            self.actual_generation += 1
            #print(self.ambient.get_grid_of_string())
            print("----------------------------------------------------")
            print("Generation:", self.actual_generation)
            print("Preys:", len(self.ambient.get_preys()))
            print("Predators:", len(self.ambient.get_predators()))
            print("Food:", len(self.ambient.get_foods()))
            print("----------------------------------------------------")
            self.mean_predators_energy()
            self.mean_predator_time_alive()
            self.mean_preys_speed()
            self.mean_prey_food_eaten()
            print("----------------------------------------------------")
            self.mean_preys_energy()
            self.mean_prey_time_alive()
            self.mean_predators_speed()
            self.mean_predator_food_eaten()
            print("----------------------------------------------------")
            #for k,v in self.ambient.get_stats_grid(4).items():
            #    print(k, v)
            #    print(" --> ratio prey:", v["preys"] / self.ambient.width * self.ambient.height / 4)
            #    print(" --> ratio predator:", v["predators"] / self.ambient.width * self.ambient.height / 4)
            #    if v["predators"] > 0:
            #        print(" --> ratio prey / predator:", v["preys"] / v["predators"])
            #   else:
            #       print(" --> ratio prey / predator:", 0)
            self.save_json()
    
    def run_generation(self):
        for _ in range(ACTIONS_IN_GENERATION):
            for predator in self.ambient.get_predators():
                predator.action(self.ambient)
                if predator.get_current_energy() == 0:
                    self.remove_dead_objects(predator)
                    #print("dead predator")
                    del predator
            for prey in self.ambient.get_preys():
                prey.action(self.ambient)
                if prey.get_current_energy() <= 0:
                    self.remove_dead_objects(prey)
                    #print("dead prey")
                    del prey

    def evaluate_fitness(self):
        for prey in self.ambient.get_preys():
            prey.update_fitness(self.actual_generation )
        for predator in self.ambient.get_predators():
            predator.update_fitness(self.actual_generation)

    def check_if_simulation_ended(self):
        if len(self.ambient.get_preys()) < 1 or len(self.ambient.get_predators()) < 1:
            self.is_simulation_ended = True

    def evolution_step(self):
        self.selection()
        l_prey = [prey for prey in self.prey_list if prey.has_eaten()]
        l_predator = [predator for predator in self.predator_list if predator.has_eaten()]
        for i in range(0, floor(len(l_prey) * PREY_BIRTHRATE )):
            prey = self.weighted_random_selection()
            self.cross_over_prey(prey)
        max_iteration = floor(len(l_predator) * PREDATOR_BIRTHRATE)
        if ( len(l_predator) > 50 ):
            max_iteration = floor(len(l_predator) * 2)
        for j in range(0, max_iteration):
            predator = self.weighted_random_selection()
            self.cross_over_predator(predator)

    def selection(self):
        #sort each creature by fitness
        self.prey_list = sorted(self.ambient.get_preys(), key=lambda prey: prey.get_fitness(), reverse=True)
        self.predator_list = sorted(self.ambient.get_predators(), key=lambda predator: predator.get_fitness(), reverse=True)

    def cross_over_prey(self, prey):
        #from self.prey_list performe weighted random selection
        if len(self.prey_list) == 0:
            return None
        creature = self.weighted_random_selection()
        if isinstance(creature, Prey):
            genome = prey.get_genome()
        else:
            assert(creature is not None)
            genome = Genome.cross_over(prey.get_genome(),creature.get_genome())
        empty_list = self.ambient.get_list_of_empty()
        random_index = randint(0, len(empty_list) - 1)
        i,j = empty_list[random_index]
        new_prey = Prey(i, j, genome, time_spawn=self.actual_generation)
        self.ambient.set_grid(i, j, new_prey)
        #print("new prey is born")

    def cross_over_predator(self, predator):
        #from self.prey_list performe weighted random selection
        if len(self.predator_list) == 0:
            return None
        creature = self.weighted_random_selection_predator()
        if isinstance(creature, Predator):
            genome = predator.get_genome()
        else:
            genome = Genome.cross_over(predator.get_genome(),creature.get_genome())
        empty_list = self.ambient.get_list_of_empty()
        random_index = randint(0, len(empty_list) - 1)
        i,j = empty_list[random_index]
        new_predator = Predator(i, j, genome, time_spawn=self.actual_generation)
        self.ambient.set_grid(i, j, new_predator)
        #print("new predator is born")

    def weighted_random_selection(self):
        weighted_list = []
        if len(self.prey_list) == 0:
            return None
        for prey in self.prey_list:
            weighted_list.append(prey.get_fitness())
        total = sum(weighted_list)
        for i in range(len(weighted_list)):
            weighted_list[i] = weighted_list[i] / total
        random_number = random()
        for i in range(len(weighted_list)):
            if random_number < weighted_list[i]:
                return self.prey_list[i]
            random_number -= weighted_list[i]
        return self.prey_list[0]
            
    def weighted_random_selection_predator(self):
        weighted_list = []
        
        if len(self.predator_list) == 0:
            return None
        for predator in self.predator_list:
            weighted_list.append(predator.get_fitness())
        total = sum(weighted_list)
        for i in range(len(weighted_list)):
            weighted_list[i] = weighted_list[i] / total
        random_number = random()
        for i in range(len(weighted_list)):
            if random_number < weighted_list[i]:
                return self.predator_list[i]
            random_number -= weighted_list[i]
        return self.predator_list[0]   

    def save_json(self):
        prey_list = []
        predator_list = []
        for prey in self.ambient.get_preys():
            prey_list.append(prey.to_json())
        for predator in self.ambient.get_predators():
            predator_list.append(predator.to_json())
        if not os.path.exists(self.log_folder + "/" + str(self.actual_generation)):
            os.makedirs(self.log_folder + "/" + str(self.actual_generation))
        prey_file = self.log_folder + "/" + str(self.actual_generation) + "/prey.json"
        predator_file = self.log_folder + "/" + str(self.actual_generation) + "/predator.json"
        with open(prey_file, 'w') as f:
            json.dump(prey_list, f)
        with open(predator_file, 'w') as f:
            json.dump(predator_list, f)

    #-------------- STATISTICS -----------------

    def mean_preys_voracity(self):
        prey_list = self.ambient.get_preys()
        prey_voracity = 0
        for prey in prey_list:
            prey_voracity += prey.get_voracity()
        if len(prey_list) == 0:
            return 0
        prey_voracity /= len(prey_list)
        print("Mean prey voracity: " + str(prey_voracity))

    def mean_predators_voracity(self):
        predator_list = self.ambient.get_predators()
        predator_voracity = 0
        for predator in predator_list:
            predator_voracity += predator.get_voracity()
        if len(predator_list) == 0:
            return 0
        predator_voracity /= len(predator_list)
        print("Mean predator voracity: " + str(predator_voracity))

    def mean_preys_speed(self):
        prey_list = self.ambient.get_preys()
        prey_speed = 0
        for prey in prey_list:
            prey_speed += prey.get_speed()
        if len(prey_list) == 0:
            return 0
        prey_speed /= len(prey_list)
        print("Mean prey speed: " + str(prey_speed))

    def mean_predators_speed(self):
        predator_list = self.ambient.get_predators()
        predator_speed = 0
        for predator in predator_list:
            predator_speed += predator.get_speed()
        if len(predator_list) == 0:
            predator_speed = 0
        else:
            predator_speed /= len(predator_list)
        print("Mean predator speed: " + str(predator_speed))

    def mean_preys_energy(self):
        prey_list = self.ambient.get_preys()
        prey_energy = 0
        for prey in prey_list:
            prey_energy += prey.get_current_energy()
        if len(prey_list) == 0:
            return 0
        prey_energy /= len(prey_list)
        print("Mean prey energy: " + str(prey_energy))

    def mean_predators_energy(self):
        predator_list = self.ambient.get_predators()
        predator_energy = 0
        for predator in predator_list:
            predator_energy += predator.get_current_energy()
        if(len(predator_list) > 0):
            predator_energy /= len(predator_list)
        else:
            predator_energy = 0
        print("Mean predator energy: " + str(predator_energy))

    def mean_preys_fitness(self):
        prey_list = self.ambient.get_preys()
        prey_fitness = 0
        for prey in prey_list:
            prey_fitness += prey.get_fitness()
        if len(prey_list) == 0:
            return 0
        prey_fitness /= len(prey_list)
        print("Mean prey fitness: " + str(prey_fitness))
    
    def mean_predators_fitness(self):
        predator_list = self.ambient.get_predators()
        predator_fitness = 0
        for predator in predator_list:
            predator_fitness += predator.get_fitness()
        if len(predator_list) == 0:
            return 0
        predator_fitness /= len(predator_list)
        print("Mean predator fitness: " + str(predator_fitness))

    def mean_prey_time_alive(self):
        prey_list = self.ambient.get_preys()
        prey_time_alive = 0
        for prey in prey_list:
            prey_time_alive += prey.get_time_alive()
        if len(prey_list) == 0:
            return 0
        prey_time_alive /= len(prey_list)
        print("Mean prey time alive: " + str(prey_time_alive))

    def mean_predator_time_alive(self):
        predator_list = self.ambient.get_predators()
        predator_time_alive = 0
        for predator in predator_list:
            predator_time_alive += predator.get_time_alive()
        if len(predator_list) == 0:
            return 0
        predator_time_alive /= len(predator_list)
        print("Mean predator time alive: " + str(predator_time_alive))

    def mean_prey_food_eaten(self):
        prey_list = self.ambient.get_preys()
        prey_food_eaten = 0
        for prey in prey_list:
            prey_food_eaten += prey.get_food_eated()
        if len(prey_list) == 0:
            return 0
        prey_food_eaten /= len(prey_list)
        print("Mean prey food eaten: " + str(prey_food_eaten))

    def mean_predator_food_eaten(self):
        predator_list = self.ambient.get_predators()
        predator_food_eaten = 0
        for predator in predator_list:
            predator_food_eaten += predator.get_food_eated()
        if len(predator_list) == 0:
            return 0
        predator_food_eaten /= len(predator_list)
        print("Mean predator food eaten: " + str(predator_food_eaten))

for _ in range(100):
    GeneticAlgotithm()