import os 
import genome
import sys
import creature
import pybullet as p
import time 
import random
import numpy as np

import env_objects

## ... usual starter code to create a sim and floor
def main(csv_file):
    assert os.path.exists(csv_file), "Tried to load " + csv_file + " but it does not exists"

    p.connect(p.GUI)
    p.setPhysicsEngineParameter(enableFileCaching=0)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

    # Implement arena, mountain, and walls in the environment
    arena = env_objects.Env_objects.make_arena()
    mountain = env_objects.Env_objects.make_mountain()
    peak = env_objects.Env_objects.get_mountain_peak(mountain)

    surrounding_walls = env_objects.Env_objects.make_surrounding_wall()

    # Add text to highlight where the peak is
    p.addUserDebugText(
        text="Peak",
        textPosition=peak,
        textColorRGB=[1, 0, 0],  # Red
        textSize=1.5,
        lifeTime=0
    )

    
    p.setGravity(0, 0, -10)
#   p.setRealTimeSimulation(1)


    # generate a random creature
    cr = creature.Creature(gene_count=1)
    dna = genome.Genome.from_csv(csv_file)
    cr.update_dna(dna)
    # save it to XML
    with open('test.urdf', 'w') as f:
        f.write(cr.to_xml())
    # load it into the sim
    rob1 = p.loadURDF('test.urdf')
    # air drop it
    p.resetBasePositionAndOrientation(rob1, [-6, -6, 2.5], [0, 0, 0, 1])
    start_pos, orn = p.getBasePositionAndOrientation(rob1)

    # iterate 
    elapsed_time = 0
    wait_time = 1.0/240 # seconds
    total_time = 30 # seconds
    step = 0
    while True:
        p.stepSimulation()
        step += 1
        if step % 24 == 0:
            motors = cr.get_motors()
            assert len(motors) == p.getNumJoints(rob1), "Something went wrong"
            for jid in range(p.getNumJoints(rob1)):
                mode = p.VELOCITY_CONTROL
                vel = motors[jid].get_output()
                p.setJointMotorControl2(rob1, 
                            jid,  
                            controlMode=mode, 
                            targetVelocity=vel)
            new_pos, orn = p.getBasePositionAndOrientation(rob1)
            # print(new_pos)
            # dist_moved = np.linalg.norm(np.asarray(start_pos) - np.asarray(new_pos))
            # print(dist_moved)

            p1 = np.asarray(new_pos)
            p2 = np.asarray(peak)
            dist = np.linalg.norm(p1-p2)

            # print(dist)

        time.sleep(wait_time)
        elapsed_time += wait_time
        if elapsed_time > total_time:
            break

    # print("TOTAL DISTANCE MOVED:", dist_moved)



if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: python playback_test.py csv_filename"
    main(sys.argv[1])

