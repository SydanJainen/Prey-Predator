from dataclasses import dataclass
import json
from random import randint, random

with open('configuration/config.json') as param_file:
    param = json.load(param_file)

    max_vision = param["genome"]['max_vision']
    min_vision = param["genome"]['min_vision']
    max_speed = param["genome"]['max_speed']
    min_speed = param["genome"]['min_speed']
    max_starting_energy = param["genome"]['max_starting_energy']
    min_starting_energy = param["genome"]['min_starting_energy']
    max_voracity = param["genome"]['max_voracity']
    min_voracity = param["genome"]['min_voracity']
    max_damage = param["genome"]['max_damage']
    min_damage = param["genome"]['min_damage']
    max_size = param["genome"]['max_size']
    min_size = param["genome"]['min_size']


    param_file.close()

class Genome:

    def __init__(self, voracity=None, speed=None, vision=None, dimension=None, starting_energy=None, damage=None):
        self.voracity : int = randint(min_voracity,max_voracity) if voracity == None else voracity
        self.speed : int = randint(min_vision,max_vision) if speed == None else speed
        self.vision : int = randint(min_vision,max_vision) if vision == None else vision
        self.dimension : int = randint(min_size,max_size) if dimension == None else dimension
        self.starting_energy : int = randint(min_starting_energy,max_starting_energy) if starting_energy == None else starting_energy
        self.damage:int = randint(min_damage,max_damage) if damage == None else damage

    def to_binary(self):
        return "{0:08b}".format(self.voracity) + "{0:08b}".format(self.speed) + "{0:08b}".format(self.vision) + "{0:08b}".format(self.dimension) + "{0:08b}".format(self.starting_energy)+ "{0:08b}".format(self.damage)


    def to_json(self):
        return {
            "voracity": self.voracity,
            "speed": self.speed,
            "vision": self.vision,
            "dimension": self.dimension,
            "starting_energy": self.starting_energy,
            "damage": self.damage
        }

    def get_max_vision(self):
        return max_vision

    def __str__(self):
        return "voracity: " + str(self.voracity) + " speed: " + str(self.speed) + " vision: " + str(self.vision) + " dimension: " + str(self.dimension) + " starting_energy: " + str(self.starting_energy) + " damage: " + str(self.damage)

    def mutation(self):
        # a random step of -1 to 1 in each attribute if the random number is less than 0.1
        if random() < 0.5:
            self.voracity += randint(-1, 1)
            if self.voracity < 0: self.voracity = 0
        if random() < 0.5:
            self.speed += randint(-1, 1)
            if self.speed < 1: self.speed = 1
        if random() < 0.5:
            self.vision += randint(-1, 1)
            if self.vision < 1: self.vision = 1
        if random() < 0.5:
            self.dimension += randint(-1, 1)
            if self.dimension < 1: self.dimension = 1
        if random() < 0.5:
            self.starting_energy += randint(-1, 1)
            if self.starting_energy < min_starting_energy: self.starting_energy = min_starting_energy
        if random() < 0.5:
            self.damage += randint(-1, 1)
            if self.damage < 1: self.damage = 1
    
    
    def save_json(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.to_json(), outfile)

    @staticmethod
    def from_binary(binary):
        voracity = int(binary[0:8], 2)
        speed = int(binary[8:16], 2)
        vision = int(binary[16:24], 2)
        dimension = int(binary[24:32], 2)
        starting_energy = int(binary[32:40], 2)
        damage = int(binary[40:48], 2)
        return Genome(voracity, speed, vision, dimension, starting_energy, damage)

    #static method cross_over
    @staticmethod
    def cross_over(first, second):
        # the first half of the genome of the first parent and the second half of the genome of the second parent
        gen  = Genome.from_binary(first.to_binary()[:20] + second.to_binary()[20:])
        gen.mutation()
        return gen        