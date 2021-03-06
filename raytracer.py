import pygame
import sys
import math
import random
import time
from vector import *
from functools import reduce

random.seed()

class Scene():
    def __init__(self, resolution, spheres, lights, camera, antialiasing):
        self.res_x, self.res_y = resolution
        self.spheres = spheres
        self.lights = lights
        self.camera = camera
        self.antialiasing = antialiasing
        self.showScreen()
    def showScreen(self):
        pygame.display.init()
        self.display = pygame.display.set_mode((self.res_x,self.res_y), 0)
    def wait(self):
        while True:
            self.checkEvents()
    def createImage(self):
        lastflip = time.time()
        self.camera.setResolution(self.res_x, self.res_y)
        for xval in range(self.res_x):
            for yval in range(self.res_y):
                rays = self.camera.rayList(xval, yval, self.antialiasing)
                #print "----------------------------------"
                #print "Tracing ray " + str(xval) +", " + str(yval)
                #print "Direction is " + str(ray.direction.vals[0])+", "+ str(ray.direction.vals[1])+", "+ str(ray.direction.vals[2])
                r = 0
                g = 0
                b = 0
                for ray in rays:
                    pixelColor = ray.trace(self.spheres, self.lights)
                    r += pixelColor.r
                    g += pixelColor.g
                    b += pixelColor.b
                self.display.set_at((xval, yval), pygame.Color(r/len(rays), g/len(rays), b/len(rays)))
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
    def trace(self, spheres, lights, recursion = 0):
        if recursion > 15:
            return pygame.Color(255, 255, 255, 0)
        #print "Analysing ray-----------------------"
        closestSphere, collidePoint = self.nearestCollision(spheres)
        if collidePoint == None:
            return pygame.Color(255, 255, 255, 0)
        collidePoint = self.origin.add(self.direction.multiply(collidePoint))
        if closestSphere == None:
            closestSphere = Sphere(collidePoint.subtract(Vector(0,1,0)), 1, Material(False, pygame.Color(200,200,200)))
        if not closestSphere.material.specular:
            returnColor = pygame.Color(0, 0, 0, 0)
            #print "Checking shadows"
            normal = collidePoint.subtract(closestSphere.origin).normalise()
            for light in lights:
                shadowRay = Ray(collidePoint.add(normal.multiply(0.01)), light.origin.subtract(collidePoint))
                shadowedBy, shadowedWhen = shadowRay.nearestCollision(spheres)  
                #Ambient
                totFromLight = pygame.Color(0, 0, 0, 0)
                totFromLight = totFromLight + scaleColor(scaleColor(closestSphere.material.color, 0.5) + scaleColor(light.color, 0.5), closestSphere.material.ka)
                #Diffuse
                if shadowedBy == None or shadowedWhen <= 0.01:
                    totFromLight = totFromLight + scaleColor(scaleColor(closestSphere.material.color, max(normal.dot(shadowRay.direction), 0.0)), closestSphere.material.kd)
                    #Specular
                    scalar = normal.dot(self.direction)
                    newDirection = normal.multiply(2*scalar)
                    newDirection = newDirection.subtract(self.direction)
                    newDirection = Vector(0,0,0).subtract(newDirection)
                    newDirection = newDirection.normalise()
                    totFromLight = totFromLight + scaleColor(light.color, pow(max(0, closestSphere.material.ks*newDirection.dot(shadowRay.direction)), closestSphere.material.shine))
                returnColor = returnColor + scaleColor(totFromLight, light.brightness)
            return returnColor
        else:
            normal = collidePoint.subtract(closestSphere.origin).normalise()
            scalar = normal.dot(self.direction)
            newDirection = normal.multiply(2*scalar)
            newDirection = newDirection.subtract(self.direction)
            newDirection = Vector(0,0,0).subtract(newDirection)
            return Ray(collidePoint.add(normal.multiply(0.01)), newDirection).trace(spheres, lights, recursion+1) - pygame.Color(20, 20, 20, 0)
            
    def nearestCollision(self, spheres):
        min_t = None
        closestSphere = None
        #collide with floor
        if self.direction.vals[1] != 0:
            floorhit = -float(self.origin.vals[1])/self.direction.vals[1]
            if floorhit > 0:
                min_t = floorhit
        for sphere in spheres:
            collide, t = self.intersect(sphere)
            if collide:
                if min_t == None:
                    min_t = t
                    closestSphere = sphere
                    #print "New closest sphere"
                elif t < min_t:
                    min_t = t
                    closestSphere = sphere
                    #print "New closest sphere"
        return closestSphere, min_t
    def intersect(self, sphere):
        #print "-- Colliding Sphere --"
        line = sphere.origin.subtract(self.origin)
        timeClosestApproach = line.dot(self.direction)
        closestApproachSquare = line.dot(line) - (timeClosestApproach * timeClosestApproach)
        #print closestApproachSquare
        #print sphere.radius * sphere.radius
        if closestApproachSquare > (sphere.radius * sphere.radius):
            #print "No collision"
            return False, 0
        #print "Collision"
        #if closestApproachSquare < 0:
            #floating point errors happen
        #    closestApproachSquare = 0
        closestApproach = math.sqrt((sphere.radius * sphere.radius) - closestApproachSquare)
        if timeClosestApproach - closestApproach >= 0:
            #print "Took nearest"
            return True, timeClosestApproach - closestApproach
        elif timeClosestApproach + closestApproach >= 0:
            #print "Took furthest"
            return True, timeClosestApproach + closestApproach
        return False, 0

class Material():
    def __init__(self, specular = False, color = pygame.Color(255, 255, 255), ka=0.5, kd=0.4, ks=0.5, shine=2):
        self.specular = specular
        self.color = color
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.shine = shine
        
        
class Sphere():
    def __init__(self, origin, radius, material):
        self.origin = origin
        self.radius = radius
        self.material = material

class LightSource():
    def __init__(self, origin, color = pygame.Color(255, 255, 255), brightness = 1.0, radius = 0):
        self.origin = origin
        self.radius = radius
        self.color = color
        self.brightness = brightness #Sum to 1.0

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
    def setResolution(self, res_x, res_y):
        self.deltax = self.imgright.normalise().divide(res_x)
        self.deltay = self.imgdown.normalise().divide(res_x)
        self.topleft = self.imgorigin.subtract(self.deltax.multiply(res_x/2))
        self.topleft = self.topleft.subtract(self.deltay.multiply(res_y/2))
        
    def rayList(self, xval, yval, antialiasing):
        pointb = self.topleft.add(self.deltax.multiply(xval))
        pointb = pointb.add(self.deltay.multiply(yval))
        pixel = []
        for minix in range(antialiasing):
            for miniy in range(antialiasing):
                pointc = pointb.add(self.deltax.multiply(float(minix)/antialiasing))
                pointc = pointc.add(self.deltay.multiply(float(miniy)/antialiasing))
                pixel.append(Ray(self.origin, pointc.subtract(self.origin)))
        return pixel

def scaleColor(color, scalar): return pygame.Color(int(color.r * scalar), int(color.g * scalar), int(color.b*scalar)) 
        
resolution = (1280, 960)        
spheres = [Sphere(Vector(0,140,100), 60, Material(True)), 
Sphere(Vector(0,40,200), 40, Material(False, pygame.Color(255,0,0))), 
Sphere(Vector(100,40,130), 40, Material(False, pygame.Color(255,255,0))), 
Sphere(Vector(100,40,70), 40, Material(False, pygame.Color(0,255,0))), 
Sphere(Vector(0,40,0), 40, Material(False, pygame.Color(0,255,255))), 
Sphere(Vector(-100,40,70), 40, Material(False, pygame.Color(0,0,255))), 
Sphere(Vector(-100,40,130), 40, Material(False, pygame.Color(255,0,255)))]
#spheres = [Sphere(Vector(0, 0, 100), 60, pygame.Color(255, 0, 0)), Sphere(Vector(-60, 0, 200), 60, pygame.Color(0, 255, 0)), Sphere(Vector(120, 0, 300), 60, pygame.Color(0, 0, 255))]
lights = [LightSource(Vector(-100, 200, -50), pygame.Color(255, 255, 255), 1.0)]
#camera = Camera(Vector(0, 80, -100), Vector(0, 0, 1), 1)
camera = Camera(Vector(0, 180, -150), Vector(0, -0.5, 1), 1)
#camera = Camera(Vector(0, 300, 200), Vector(0, -1, 0), 0.5)
antialiasing = 3

Scene(resolution, spheres, lights, camera, antialiasing).createImage()