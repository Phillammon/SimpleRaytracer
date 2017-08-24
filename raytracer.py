import pygame
import sys
import math
import random
import time
from vector import *
from functools import reduce

random.seed()

class Scene():
    def __init__(self, resolution, spheres, lights, camera):
        self.res_x, self.res_y = resolution
        self.spheres = spheres
        self.lights = lights
        self.camera = camera
        self.showScreen()
    def showScreen(self):
        pygame.display.init()
        self.display = pygame.display.set_mode((self.res_x,self.res_y), 0)
    def wait(self):
        while True:
            self.checkEvents()
    def createImage(self):
        lastflip = time.time()
        for xval, yval, ray in self.camera.rayList(self.res_x, self.res_y):
            #print "----------------------------------"
            #print "Tracing ray " + str(xval) +", " + str(yval)
            #print "Direction is " + str(ray.direction.vals[0])+", "+ str(ray.direction.vals[1])+", "+ str(ray.direction.vals[2])
            self.display.set_at((xval, yval), ray.trace(spheres))
            if time.time()-lastflip > 0.015:
                pygame.display.update()
                lastflip = time.time()
            self.checkEvents()
        #print "Done!"
        pygame.display.update()
        self.wait()
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #sys.exit()
				
class Ray():
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalise()
    def trace(self, spheres):
        closestSphere = self.nearestCollision(spheres)
        if closestSphere == None:
            return pygame.Color(255, 255, 255, 0)
        return closestSphere.color
    def nearestCollision(self, spheres):
        min_t = None
        closestSphere = None
        for sphere in spheres:
            collide, t = self.intersect(sphere)
            if collide:
                if min_t == None:
                    min_t = t
                    closestSphere = sphere
                    #print "New closest sphere"
                elif t < min_t and t > 0:
                    min_t = t
                    closestSphere = sphere
                    #print "New closest sphere"
                elif t > 0:
                    #print "Not closest collision"
                    pass
                else:
                    #print "Behind camera"
                    pass
        return closestSphere
    def intersect(self, sphere):
        #print "-- Colliding Sphere --"
        origins = sphere.origin.subtract(self.origin)
        closestApproachUnits = origins.dot(self.direction)
        closestApproachSquare = origins.dot(origins) - (closestApproachUnits * closestApproachUnits)
        #print closestApproachSquare
        #print sphere.radius * sphere.radius
        if closestApproachSquare > sphere.radius * sphere.radius:
            #print "No collision"
            return False, 0
        #print "Collision"
        if closestApproachSquare < 0:
            #floating point errors happen
            closestApproachSquare = 0
        closestApproach = math.sqrt(closestApproachSquare)
        if closestApproachUnits - closestApproach > 0:
            return True, closestApproachUnits - closestApproach
        return True, closestApproachUnits + closestApproach
        
        
class Sphere():
    def __init__(self, origin, radius, color):
        self.origin = origin
        self.radius = radius
        self.color = color

class Camera():
    def __init__(self, origin, direction, length):
        self.origin = origin
        self.direction = direction.normalise()
        self.imgorigin = self.origin.add(self.direction.multiply(length))
        if self.direction.vals[2] != 0:
            xz = self.direction.vals[0] / self.direction.vals[2]
            if xz == 0:
                self.imgdown = Vector(1, 0, 0).cross(self.direction)
            else:
                xznr = -1.0 / xz
                self.imgdown = Vector(xznr, 0, 1).cross(self.direction)
        else:
            self.imgdown = Vector(0, 0, 1).cross(self.direction)
        imgup = Vector(0, 0, 0).subtract(self.imgdown)
        self.imgright = imgup.cross(self.direction)
    def rayList(self, res_x, res_y):
        returnlist = []
        deltax = self.imgright.normalise().divide(res_x)
        deltay = self.imgdown.normalise().divide(res_x)
        topleft = self.imgorigin.subtract(deltax.multiply(res_x/2))
        topleft = topleft.subtract(deltay.multiply(res_y/2))
        #print str(deltax.vals[0]) + "," + str(deltax.vals[1]) + "," + str(deltax.vals[2])
        #print str(deltay.vals[0]) + "," + str(deltay.vals[1]) + "," + str(deltay.vals[2])
        for xval in range(res_x):
            for yval in range(res_y):
                pointb = topleft.add(deltax.multiply(xval))
                pointb = pointb.add(deltay.multiply(yval))
                returnlist.append([xval, yval, Ray(self.origin, pointb.subtract(self.origin))])
        return returnlist

        
resolution = (640, 480)        
spheres = [Sphere(Vector(0, 60, 100), 60, pygame.Color(255, 0, 0)), Sphere(Vector(-60, 60, 200), 60, pygame.Color(0, 255, 0)), Sphere(Vector(120, 60, 300), 60, pygame.Color(0, 0, 255))]
lights = [Sphere(Vector(0, 200, 200), 0, pygame.Color(255, 255, 255))]
camera = Camera(Vector(0, 80, -100), Vector(0, 0, 1), 1)

Scene(resolution, spheres, lights, camera).createImage()