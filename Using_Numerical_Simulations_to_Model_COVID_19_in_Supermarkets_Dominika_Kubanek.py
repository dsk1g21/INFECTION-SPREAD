# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 16:19:01 2024

@author: Dominika Kubanek
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skewnorm

p = 235  # number of people in the simulation
n = 5000  # maximum number of steps taken by each person
num_infected = 1
N = 65  # dimensions of shop
repeat = 2000

probability_unmasked = 0.5 # for over 41 
probability_of_mask = 0.34 # surgical mask probability (66% decrease)
probability_of_distance = 0.128 # for 2m separation
probability_of_mask_and_unmask = probability_of_mask * probability_unmasked
probability_of_all = probability_unmasked * probability_of_mask * probability_of_distance
probability_unmasked_with_distancing = probability_of_distance * probability_unmasked

def check_object(pos):
    '''
    Creates the obstables from the shop
    
    Checks whether person coordinates are inside the vertices of the obstacles.
    '''
    vertices = [[10, 0], [40, 0], [0, 58], [65, 20], [40, 19], [40, 25], [40, 31], [40, 37], [40, 43], [40, 49], [40, 55], [40, 61], [40, 67], [5, 24], [5, 30.5], [5, 37], [5, 43.5], [5, 50], [4, 13], [15, 13]]
    widths = [20, 29, 20, 4, 21, 21, 21, 21, 21, 21, 21, 21, 21, 18, 18, 18, 18, 18, 8, 8]
    heights = [5, 10, 11, 49, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1.5, 1.5, 1.5, 1.5, 1.5, 5, 5]
    for i , vert in enumerate(vertices):
        min_x , min_y = vert[0] , vert[1]
        max_x , max_y = vert[0] + widths[i] , vert[1] + heights[i]
        return (min_x <= pos[0] <= max_x) and (min_y <= pos[1] <= max_y)

class Person():
    def __init__(self):
        '''
        initialises each person in the simulation
        '''
        self.x = 0
        self.y = 0
        pos = [self.x , self.y]
        while check_object(pos) is True:
            self.x = np.random.uniform(0 , 65)
            self.y = np.random.uniform(0 , 65)
            pos = [self.x , self.y]
        self.angle = 0  # angle of movement
        self.infected = False       

    def move(self , positions):
        '''
        gives each person a random angle to move at
        
        tests whether move is valid by checking if they are within the shop dimensions
        and whether each person stays 2m apart. If move invalid redefines angle of motion
        '''
        valid_move = False
        while valid_move == False:
            self.angle = 2 * np.pi * np.random.random()
            dx = np.cos(self.angle)
            dy = np.sin(self.angle)
            next_x = self.x + dx
            next_y = self.y + dy
            if 0 < next_x < N and 0 < next_y < N:
                self.x = next_x
                self.y = next_y
            for pos in positions:
                if not (pos[0] == self.x and pos[1] == self.y): # if we're not checking against ourself
                    dx = abs(pos[0] - self.x)
                    dy = abs(pos[1] - self.y)
                    if np.sqrt(dx**2 + dy**2) > 2:
                        valid_move = True
  
class ShopSimulation():
    def __init__(self):
        self.num_people = p
        self.num_steps = n
        self.num_infected = num_infected
        self.dimensions = N
        self.people = []
        self.setup_shop()
        self.infect_people()
        self.infections_probability = probability_unmasked
 
    def setup_shop(self):
        '''
        initiallises each persons position in the shop and makes a list of each of them
        '''
        for _ in range(self.num_people):
            person = Person()
            person.x = np.random.uniform(0, N)
            person.y = np.random.uniform(0, N)
            self.people.append(person)
 
    def infect_people(self):
        '''
        at random chooses one person to have COVID at the beginning of the simulation
        '''
        infected_indices = np.random.choice(range(self.num_people), self.num_infected, replace=False)
        for index in infected_indices:
            self.people[index].infected = True
    
    def simulate(self):
        '''
        Updates the movements of each person until every person in the simulation has
        been 'infected' at which point it counts the number of steps required 
        
        Checks if people have been infected using the check_collision function.        
        '''
        for step in range(self.num_steps):
            people_positions = []
            for person in self.people:
                people_positions.append([person.x , person.y])
                person.move(people_positions)
            self.check_collisions()  # Check for collisions between infected and non-infected people
            if len([person for person in self.people if person.infected]) == p:
                return step + 1  # Return the number of steps taken
        return self.num_steps  # If not all infected, return the total number of steps
 
    def check_collisions(self):
        '''
        tests if people are infected by checking each persons distance from infected people
        and if they are less than 2.1m apart they can be infected.
        '''
        for i, person in enumerate(self.people):
            if person.infected:  # Check collisions only for infected people
                for j, other_person in enumerate(self.people):
                    if not other_person.infected:  # Check collisions only with non-infected people
                        distance = np.sqrt((person.x - other_person.x)**2 + (person.y - other_person.y)**2)
                        if distance <= 2.1:  # If the distance is less than 4 (radius of the infected person's circle)
                            if np.random.random() < self.infections_probability:
                                other_person.infected = True  # Mark the non-infected person as infected
 
# Create and simulate the shop
number_of_steps_to_infect_all = []
for step in range(repeat):
    shop = ShopSimulation()
    steps_taken = shop.simulate()
    number_of_steps_to_infect_all.append(steps_taken)
    print(f'Trial %s'%step , number_of_steps_to_infect_all)

print(number_of_steps_to_infect_all)
params = skewnorm.fit(number_of_steps_to_infect_all)
shape, loc, scale = params

scale_factor = 1.6
new_scale = scale * scale_factor
new_params = (shape, loc, new_scale)

delta = shape / np.sqrt(1 + shape**2)

std = scale * np.sqrt(1 - (2 * delta**2) / np.pi)

mu = loc + scale * delta * np.sqrt(2 / np.pi)

new_data = skewnorm.rvs(*new_params, size=1000)

lower_percentile = skewnorm.ppf(0.0015, shape, loc, scale)
upper_percentile = skewnorm.ppf(0.9985, shape, loc, scale)
print(f'99.7% of the data lies between {lower_percentile:.2f} and {upper_percentile:.2f}')

plt.figure(figsize=(10, 6))
plt.hist(new_data, bins=38, density=True, alpha=0.6, color='plum', label='Adjusted data')

x = np.linspace(min(number_of_steps_to_infect_all), max(number_of_steps_to_infect_all), 2000)

plt.plot(x, skewnorm.pdf(x, *new_params), color='steelblue', lw=2, label='Adjusted distribution')
plt.plot(x, skewnorm.pdf(x, *new_params), color='steelblue', lw=2, label=r'$\mu = %f$'%mu)
plt.plot(x, skewnorm.pdf(x, *new_params), color='steelblue', lw=2, label=r'$\sigma = %f$'%std)
plt.title('Adjusted distribution of unmasked with no social distancing')
plt.xlabel('Number of steps to infect all')
plt.ylabel('Frequency')
plt.legend(fontsize=15)
plt.show()