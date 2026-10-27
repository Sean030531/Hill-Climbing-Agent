import creature 
import numpy as np

import pybullet as p
import env_objects

class Population:
    def __init__(self, pop_size, gene_count):
        self.creatures = [creature.Creature(
                          gene_count=gene_count) 
                          for i in range(pop_size)]
        # Record the closest distance to peak
        self.min_dist_to_peak = None

    @staticmethod
    def get_fitness_map(fits):
        fitmap = []
        total = 0
        for f in fits:
            total = total + f
            fitmap.append(total)
        return fitmap
    
    @staticmethod
    def select_parent(fitmap):
        r = np.random.rand() # 0-1
        r = r * fitmap[-1]
        for i in range(len(fitmap)):
            if r <= fitmap[i]:
                return i
            
    # Baseline fitness function
    def fitness_function_baseline(self):
        # Get peak z coordinate
        p.connect(p.DIRECT)
        mountain = env_objects.Env_objects.make_mountain()
        peak = env_objects.Env_objects.get_mountain_peak(mountain)

        # Calculate the distance between creature and the peak
        fits = [cr.get_to_peak_distance(peak) 
                for cr in self.creatures]
        
        # Define the diagonal distance between the corner of the arena and peak as max distance
        max_distance = np.linalg.norm(np.asarray([-10,-10,0])-np.asarray(peak))
        
        # Subtract fits with max distance
        fits = max_distance - fits
        
        return fits

    # Improved fitness function
    def improved_finess_function(self):
        # Get peak z coordinate
        p.connect(p.DIRECT)
        mountain = env_objects.Env_objects.make_mountain()
        peak = env_objects.Env_objects.get_mountain_peak(mountain)

        # Calculate the distance between creature and the peak
        dist_to_peak = [cr.get_to_peak_distance(peak) 
                        for cr in self.creatures]
        
        # Update the closest distance to peak
        if self.min_dist_to_peak == None:
            self.min_dist_to_peak = np.min(dist_to_peak)
        elif self.min_dist_to_peak > np.min(dist_to_peak):
            self.min_dist_to_peak = np.min(dist_to_peak)
            
        # Define the diagonal distance between the corner of the arena and peak as max distance
        max_distance = np.linalg.norm(np.asarray([-8,-8,0])-np.asarray(peak))
        # Subtract fits with max distance
        dist_to_peak = max_distance - dist_to_peak

        # Calculate the creature size
        body_size = np.asarray([cr.get_cr_size() 
                                for cr in self.creatures])
        
        # Calculate the net climbing score
        uphill_score = np.asarray([cr.get_uphill_score() 
                                   for cr in self.creatures])

        # Compute the milestone bonuses, 75% height get 5; 100% height get 10
        peak_z = peak[2]
        thresholds    = [0.75*peak_z, 1.00*peak_z]
        bonus_weights = [5.0, 10.0]
        bh = [cr.get_max_height() 
              for cr in self.creatures]

        bonuses = []
        for h in bh:
            b = 0.0
            for thr, w in zip(thresholds, bonus_weights):
                if h >= thr:
                    b += w
            bonuses.append(b)        

        bonuses = np.array(bonuses)

        # Different factor weight control. Comment out those don't need
        size_w, up_w = -0.3, 0.3
        # size_w, up_w = -0.4, 0.3
        # size_w, up_w = -0.5, 0.3
        # size_w, up_w = -0.8, 0.3
        # size_w, up_w = -0.3, 0.5
        # size_w, up_w = -0.5, 0.5
        # size_w, up_w = -0.8, 0.5
        # size_w, up_w = -0.3, 0.8
        # size_w, up_w = -0.5, 0.8
        # size_w, up_w = -0.8, 0.8

        # Fits with bonuses
        # fits = dist_to_peak + size_w*body_size + up_w*uphill_score + bonuses

        # Fits without bonuses
        fits = dist_to_peak + size_w*body_size + up_w*uphill_score
        return fits.tolist()        