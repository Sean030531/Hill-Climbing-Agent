# If you on a Windows machine with any Python version 
# or an M1 mac with any Python version
# or an Intel Mac with Python > 3.7
# the multi-threaded version does not work
# so instead, you can use this version. 

import unittest
import population
import simulation_surrounding_walls
import genome 
import creature 
import numpy as np

import os

class TestGA(unittest.TestCase):
    def testBasicGA(self):
        pop = population.Population(pop_size=10, 
                                    gene_count=3)
        #sim = simulation.ThreadedSim(pool_size=1)
        sim = simulation_surrounding_walls.Simulation()

        # Record mertics
        generation_fitness_data = []
        generation_link_data = []
        generation_to_peak_data = []

        for iteration in range(300):
            # this is a non-threaded version 
            # where we just call run_creature instead
            # of eval_population  
            sim.eval_population(pop, 2400)

            # Improved fitness function
            fits = pop.improved_finess_function()

            links = [len(cr.get_expanded_links()) 
                    for cr in pop.creatures]
            
            # Record mertics
            generation_fitness_data.append(np.round(np.max(fits), 3))
            generation_link_data.append(np.round(np.max(links)))
            generation_to_peak_data.append(pop.min_dist_to_peak)

            print(iteration, "fittest:", np.round(np.max(fits), 3), 
                  "mean:", np.round(np.mean(fits), 3), "mean links", np.round(np.mean(links)), "max links", np.round(np.max(links)))       
            fit_map = population.Population.get_fitness_map(fits)
            new_creatures = []
            for i in range(len(pop.creatures)):
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                # now we have the parents!
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
                dna = genome.Genome.shrink_mutate(dna, rate=0.25)
                dna = genome.Genome.grow_mutate(dna, rate=0.1)
                cr = creature.Creature(1)
                cr.update_dna(dna)
                new_creatures.append(cr)
            # elitism
            max_fit = np.max(fits)

            for i, cr in enumerate(pop.creatures):
                if fits[i] == max_fit:
                    new_cr = creature.Creature(1)
                    new_cr.update_dna(cr.dna)
                    new_creatures[0] = new_cr

                    # Put csv files in the elites folder
                    os.makedirs("elites", exist_ok=True)
                    filename = os.path.join("elites", f"elite_{iteration}.csv")
                    genome.Genome.to_csv(cr.dna, filename)
                    break
            
            pop.creatures = new_creatures
            
        # Print mertics
        print("Average Fitness:", np.round(np.mean(generation_fitness_data), 3))
        print("Best Fitness:", np.round(np.max(generation_fitness_data), 3))
        
        print("Max Links:", np.round(np.max(generation_link_data), 3))

        print("Min Distance to Peak:", np.round(np.min(generation_to_peak_data), 3))
                            
        self.assertNotEqual(fits[0], 0)

unittest.main()
