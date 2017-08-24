import math
        
class Vector():
    def __init__(self, *args):
        if isinstance(args[0], list):
            self.vals = args[0]
        else:
            self.vals = list(args)
    def magnitude(self):
        return math.sqrt(sum(v*v for v in self.vals))
    def normalise(self):
        return Vector(map(lambda v: v/self.magnitude(), self.vals))
    def cross(self, vec2):
        return Vector(self.vals[1]*vec2.vals[2]-self.vals[2]*vec2.vals[1],
        self.vals[2]*vec2.vals[0]-self.vals[0]*vec2.vals[2],
        self.vals[0]*vec2.vals[1]-self.vals[1]*vec2.vals[0])
    def dot(self, vec2):
        return sum([i*j for (i, j) in zip(self.vals, vec2.vals)])
    def theta(self, vec2):
        return math.acos(self.dot(vec2)/(self.magnitude()*vec2.magnitude()))
    def add(self, vec2):
        return Vector(map(lambda (i, j): i+j, zip(self.vals, vec2.vals)))
    def subtract(self, vec2):
        return Vector(map(lambda (i, j): i-j, zip(self.vals, vec2.vals)))
    def multiply(self, scalar):
        return Vector(map(lambda v: v * scalar, self.vals))
    def divide(self, scalar):
        return self.multiply(1.0/scalar)