import pygame
import sys
import math
import random
import time

random.seed()


class Scene():
    def __init__(self, resolution, spheres, planes, lights, viewpoint, image):
        self.res_x, self.res_y = resolution
        self.spheres = spheres
        self.planes = planes
        self.lights = lights
        self.viewpoint = viewpoint
        self.image = image
        self.showScreen()
    def showScreen(self):
        pygame.display.init()
        self.display = pygame.display.set_mode((self.res_x,self.res_y), 0)
    def wait(self):
        while True:
            self.checkEvents()
    def createImage(self):
        lastflip = time.time()
        deltax = self.image.width/self.res_x
        deltay = 1.0/self.res_y
        for xval in range(self.res_x):
            for yval in range(self.res_y):
                ray = Ray(self, [self.viewpoint.x, self.viewpoint.y, self.viewpoint.z], [self.image.x - (self.res_x/2) +(xval * deltax), self.image.y- (self.res_y/2) +(yval * deltay), self.image.z])
                self.display.set_at((xval, yval), ray.trace())
                if time.time()-lastflip > 0.015:
                    pygame.display.update()
                    lastflip = time.time()
                self.checkEvents()
        pygame.display.update()
        self.wait()
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

class Sphere():
    def __init__(self, x, y, z, radius, color):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.color = color

class Plane():
    def __init__(self, x=None, y=None, z = None, color = pygame.Color(255, 255, 255, 0)):
        self.x = x
        self.y = y
        self.z = z
        self.color = color

class LightSource():
    def __init__(self, x=None, y=None, z = None):
        self.x = x
        self.y = y
        self.z = z
        
class Image():
    def __init__(self, x, y, z, width):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        
class Viewpoint():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
class Ray():
    def __init__(self, scene, point_a, point_b):
        self.scene = scene
        self.position = point_a
        self.delta = self.normalise([a - b for a, b in zip(point_a, point_b)])
    def magnitude(self, vector):
        return math.sqrt(sum(vector[i]*vector[i] for i in range(len(vector))))
    def normalise(self, vector):
        m=self.magnitude(vector)
        return [val/m for val in vector]
    def trace(self):
        return pygame.Color(random.randrange(255),random.randrange(255),random.randrange(255),0)
        

resolution = (640, 480)
spheres = [Sphere(0, 60, 200, 60, pygame.Color(255,0,0,0)),Sphere(50, 60, 150, 60, pygame.Color(0,255,0,0)),Sphere(100, 60, 100, 60, pygame.Color(0,0,255,0))]
planes = [Plane(y = 0, color = pygame.Color(180,180,180,0)), Plane(y = 250), Plane(z = 250), Plane(z = -100), Plane(x = -100), Plane(x = 200)]
lights = [LightSource(50, 200, 150)]
viewpoint = Viewpoint(50, 100, 0)
image = Image(50, 100, 10, 6.4)
        
Scene(resolution, spheres, planes, lights, viewpoint, image).createImage()