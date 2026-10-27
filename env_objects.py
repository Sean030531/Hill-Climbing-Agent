import pybullet as p
import pybullet_data
import numpy as np
import random

import math

class Env_objects:
    # Create Arena, adapt the code from cw-envt.py
    @staticmethod
    def make_arena(arena_size=20, wall_height=3, physicsClientId=None):
        # build the extra‐args dict
        extra = {}
        if physicsClientId is not None:
            extra["physicsClientId"] = physicsClientId

        wall_thickness = 0.5
        floor_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, arena_size/2, wall_thickness], **extra)
        floor_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, arena_size/2, wall_thickness], rgbaColor=[1, 1, 0, 1], **extra)
        floor_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=floor_collision_shape, baseVisualShapeIndex=floor_visual_shape, basePosition=[0, 0, -wall_thickness], **extra)

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, wall_thickness/2, wall_height/2], **extra)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, wall_thickness/2, wall_height/2], rgbaColor=[0.7, 0.7, 0.7, 1], **extra)  # Gray walls

        # Create four walls
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[0, arena_size/2, wall_height/2], **extra)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[0, -arena_size/2, wall_height/2], **extra)

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[wall_thickness/2, arena_size/2, wall_height/2], **extra)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[wall_thickness/2, arena_size/2, wall_height/2], rgbaColor=[0.7, 0.7, 0.7, 1], **extra)  # Gray walls

        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[arena_size/2, 0, wall_height/2], **extra)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[-arena_size/2, 0, wall_height/2], **extra)


    # Create Mountain, adapt the code from cw-envt.py
    @staticmethod
    def make_mountain(path="shapes/gaussian_pyramid.urdf", physicsClientId = None):
        # build the extra‐args dict
        extra = {}
        if physicsClientId is not None:
            extra["physicsClientId"] = physicsClientId
            
        mountain_position = (0, 0, 0)
        mountain_orientation = p.getQuaternionFromEuler((0, 0, 0))
        mountain = p.loadURDF(path, mountain_position, mountain_orientation, useFixedBase=1, **extra)
        return mountain

    # Get mountain peak z coordinate
    @staticmethod
    def get_mountain_peak(mountain):
        aabb_min, aabb_max = p.getAABB(mountain)

        return (0, 0, aabb_max[2])
    
    # Create walls around spawn zone
    @staticmethod
    def make_surrounding_wall(physicsClientId = None):
        # build the extra‐args dict
        extra = {}
        if physicsClientId is not None:
            extra["physicsClientId"] = physicsClientId

        # Wall parameters
        wall_thickness = 0.5
        wall_width = 10
        wall_height = 5
  
        # Wall rotation value
        right_wall_orientation_quaternion = p.getQuaternionFromEuler([0, math.radians(-25), math.radians(-20)])
        left_wall_orientation_quaternion = p.getQuaternionFromEuler([0, math.radians(25), math.radians(-60)])
        behind_wall_orientation_quaternion = p.getQuaternionFromEuler([0, 0, math.radians(45)])

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, 
                                                      halfExtents=[wall_thickness/2, wall_width/2, wall_height/2], 
                                                      **extra)
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, 
                                                halfExtents=[wall_thickness/2, wall_width/2, wall_height/2], 
                                                rgbaColor=[0, 0, 1, 1], 
                                                **extra)  # Gray walls

        # Create right wall
        p.createMultiBody(baseMass=0, 
                          baseCollisionShapeIndex=wall_collision_shape, 
                          baseVisualShapeIndex=wall_visual_shape, 
                          basePosition=[-7, -3, wall_height/2], 
                          baseOrientation=right_wall_orientation_quaternion,
                          **extra)
        
        # Create left wall
        p.createMultiBody(baseMass=0, 
                          baseCollisionShapeIndex=wall_collision_shape, 
                          baseVisualShapeIndex=wall_visual_shape, 
                          basePosition=[-3, -7, wall_height/2], 
                          baseOrientation=left_wall_orientation_quaternion,
                          **extra)
        
        # Create behind wall
        p.createMultiBody(baseMass=0, 
                          baseCollisionShapeIndex=wall_collision_shape, 
                          baseVisualShapeIndex=wall_visual_shape, 
                          basePosition=[-7, -7, wall_height/2], 
                          baseOrientation=behind_wall_orientation_quaternion,
                          **extra)