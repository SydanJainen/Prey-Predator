import matplotlib
import os
import sys 
import json

FOLDER = "./log/"
folders = os.listdir(FOLDER)
preys : map = {}
predators : map= {}
hp = {}

prey_mean_starting_energy = 0
prey_mean_velocity = 0
predator_mean_starting_energy = 0
predator_mean_velocity = 0
prey_count_per_gen = 0
i = 0
j = 0
for folder in folders:
    with open(FOLDER + folder + "/log.json") as f:
        hp.update({folder: json.load(f)})
    generations = os.listdir(FOLDER + folder)
    folder_prey = {}
    folder_predator = {}
    for generation in generations:
        if generation == "log.json":
            continue
        with open(FOLDER + folder +"/"+ generation + "/prey.json") as prey_file:
            prey = json.load(prey_file)
            folder_prey.update({generation: prey})
        with open(FOLDER + folder +"/"+ generation  + "/predator.json") as predator_file:
            predator = json.load(predator_file)
            folder_predator.update({generation: predator})
    preys.update({folder: folder_prey})
    predators.update({folder: folder_predator})

for prey in preys:
    for generation in preys[prey]:
        elements : map = preys[prey][generation] 
        for element in elements:
            prey_mean_starting_energy += element["genome"]["starting_energy"]
            prey_mean_velocity += element["genome"]["speed"]
            i += 1
            prey_count_per_gen += 1
        prey_count_per_gen = 0
for predator in predators:
    for generation in predators[predator]:
        elements : map = predators[predator][generation] 
        for element in elements:
            predator_mean_starting_energy += element["genome"]["starting_energy"]
            predator_mean_velocity += element["genome"]["speed"]
            j += 1

prey_mean_starting_energy /= i
prey_mean_velocity /= i
predator_mean_starting_energy /= j
predator_mean_velocity /= j

print("Starting Energy Mean: " + str(prey_mean_starting_energy))
print("Velocity Mean: " + str(prey_mean_velocity))
print("Starting Energy Mean: " + str(predator_mean_starting_energy))
print("Velocity Mean: " + str(predator_mean_velocity))
print("Total runs: " + str(len(folders)))

# plot some data
import matplotlib.pyplot as plt
import numpy as np

#parametrization of plot function
def plot (param, folder, color , label, name ):
    y = []
    for k,v in folder.items():
        # check exist of prey
        l = 0
        for element in v:
            l += element["genome"][param]
        if len(v) > 0:
            y.append(l/len(v))
    x = np.arange(len(y))
    # legend
    plt.plot(x, y, color, label=label)
    # x axis legend is time
    plt.xlabel("time")
    # y axis legend is vision
    plt.ylabel(param)
    plt.plot(x, y, color)
    #save the plot
    #plt.draw()
    plt.savefig("images/predator/"+name + ".png", dpi = 1000)
    #plt.show()
    #clear the plot
    plt.clf()


#for single_run in preys:
#    plot("starting_energy", preys[single_run], "r", "prey starting energy", "prey_starting_energy_"+single_run)
#    plot("speed", preys[single_run], "r", "prey speed", "prey_speed_"+single_run)
#    plot("dimension", preys[single_run], "r", "prey dimension", "prey_dimension_"+single_run)
#    plot("vision", preys[single_run], "r", "prey vision", "prey_vision_"+single_run)

for single_run in predators:
    plot("starting_energy", predators[single_run], "b", "predator starting energy", "predator_starting_energy_"+single_run)
    plot("speed", predators[single_run], "b", "predator speed", "predator_speed_"+single_run)
    plot("dimension", predators[single_run], "b", "predator dimension", "predator_dimension_"+single_run)
    plot("vision", predators[single_run], "b", "predator vision", "predator_vision_"+single_run)