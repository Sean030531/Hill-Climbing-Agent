import genome 
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np

import pybullet as p
import env_objects

class MotorType(Enum):
    PULSE = 1
    SINE = 2
    # Add 2 more motor type
    SAWTOOTH = 3
    NOISE = 4

class Motor:
    def __init__(self, control_waveform, control_amp, control_freq):
        # Evenly distribute control_waveform value to a motor type
        # Comment out this section if testing specific motor type
        if control_waveform <= 0.25:
            self.motor_type = MotorType.PULSE
        elif control_waveform <= 0.50:
            self.motor_type = MotorType.SINE
        elif control_waveform <= 0.75:
            self.motor_type = MotorType.SAWTOOTH
        else:
            self.motor_type = MotorType.NOISE

        # Testing specific motor type
        # Comment out this section if want to choose motor type randomly
        # self.motor_type = MotorType.PULSE
        # self.motor_type = MotorType.SINE
        # self.motor_type = MotorType.SAWTOOTH
        # self.motor_type = MotorType.NOISE

        self.amp = control_amp
        self.freq = control_freq
        self.phase = 0
    

    def get_output(self):
        self.phase = (self.phase + self.freq) % (np.pi * 2)
        if self.motor_type == MotorType.PULSE:
            if self.phase < np.pi:
                output = 1
            else:
                output = -1
            
        if self.motor_type == MotorType.SINE:
            output = np.sin(self.phase)

        # Implement sawtooth
        if self.motor_type == MotorType.SAWTOOTH:
            output = ((self.phase / (np.pi * 2)) * 2 - 1)

        # Implement noise
        if self.motor_type == MotorType.NOISE:
            output = np.random.uniform(-1, 1)
        
        return output 

class Creature:
    def __init__(self, gene_count):
        self.spec = genome.Genome.get_gene_spec()
        self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None

        # Record the max height and net climbing score
        self.max_height = None
        self.uphill_score = 0


    def get_flat_links(self):
        if self.flat_links == None:
            gdicts = genome.Genome.get_genome_dicts(self.dna, self.spec)
            self.flat_links = genome.Genome.genome_to_links(gdicts)
        return self.flat_links
    
    def get_expanded_links(self):
        self.get_flat_links()
        if self.exp_links is not None:
            return self.exp_links
        
        exp_links = [self.flat_links[0]]
        genome.Genome.expandLinks(self.flat_links[0], 
                                self.flat_links[0].name, 
                                self.flat_links, 
                                exp_links)
        self.exp_links = exp_links
        return self.exp_links

    def to_xml(self):
        self.get_expanded_links()
        domimpl = getDOMImplementation()
        adom = domimpl.createDocument(None, "start", None)
        robot_tag = adom.createElement("robot")
        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))
        first = True
        for link in self.exp_links:
            if first:# skip the root node! 
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))
        robot_tag.setAttribute("name", "pepe") #  choose a name!
        return '<?xml version="1.0"?>' + robot_tag.toprettyxml()

    def get_motors(self):
        self.get_expanded_links()
        if self.motors == None:
            motors = []
            for i in range(1, len(self.exp_links)):
                l = self.exp_links[i]
                m = Motor(l.control_waveform, l.control_amp,  l.control_freq)
                motors.append(m)
            self.motors = motors 
        return self.motors 
    
    def update_position(self, pos):
        z = pos[2]
        if self.start_position == None:
            self.start_position = pos
        else:
            self.last_position = pos
            # Calculate the net climbing score
            dz = z - self.last_position[2]
            if dz > 0:
                self.uphill_score += dz

        # Updating the max height
        if self.max_height == None:
            self.max_height = z
        if z > self.max_height:
            self.max_height = z
        
    def get_distance_travelled(self):
        if self.start_position is None or self.last_position is None:
            return 0
        p1 = np.asarray(self.start_position)
        p2 = np.asarray(self.last_position)
        dist = np.linalg.norm(p1-p2)
        return dist 

    def update_dna(self, dna):
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None

        # Update the max height and net climbing score
        self.max_height = None
        self.uphill_score = 0

    # Calculate the distance between creature and the peak
    def get_to_peak_distance(self, peak):
        if self.start_position is None or self.last_position is None:
            return 0
        p1 = np.asarray(self.last_position)
        p2 = np.asarray(peak)
        dist = np.linalg.norm(p1-p2)
        return dist 
    
    # Gets the link of the creature
    def get_cr_link(self):
        return len(self.exp_links)
    
    # Gets the creature size
    def get_cr_size(self):
        volume = 0.0
        for gene in self.dna:
            l = gene[1]
            r = gene[2]
            link_volume = np.pi * (r ** 2) * l
            volume += link_volume

        return volume
    
    # Get the max height
    def get_max_height(self):
        return self.max_height
    
    # Get the net climbing score
    def get_uphill_score(self):
        return self.uphill_score


