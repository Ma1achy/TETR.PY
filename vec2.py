import numpy as np
class Vec2():
    def __init__(self, x, y):
        """
        Construct a 2D vector (x , y)
        
        args:
        x (float): the x component of the vector
        y (float): the y component of the vector
        """
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"<Vec2 | x={self.x} y={self.y}>" #define how the vector is printed
        
    def __truediv__(self, scalar): #define division by a scalar
        return Vec2(self.x/scalar , self.y/scalar) 
    
    def __add__(self, vec): #define vector addition
        return Vec2(self.x + vec.x , self.y + vec.y)
    
    def __sub__(self, vec): #define subtraction between vectors
        return Vec2((self.x - vec.x) , (self.y - vec.y))
    
    def magnitude(self): #define the magnitude of a vector
        return np.sqrt(self.x**2 + self.y**2)
    
    def normalise(a): #normalise a vector
        return a / a.magnitude()
    
    def __mul__(self, scalar): #define multipication by a scalar
        return Vec2(self.x * scalar, self.y * scalar)
    
    def distance(a, b): #define the distance between two vectors
        return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)