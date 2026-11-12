class Raindrop:
    def __init__(self, x,y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def step(self, dt):
        self.y = self.y -self.speed*dt

    def on_ground(self):
         return self.y <= 0

class Person:
    def __init__(self, speed, width=0.3, height=1.8):
        self.speed = speed
        self.width = width
        self.height = height
        self.x = 0.0
    def step(self, dt):
        self.x = self.x +self.speed*dt
    def is_hit(self, drop):
        return self.x <= drop.x <= self.x + self.width and 0 <= drop.y <= self.height
        
p = Person(speed=2.0)

print(p.is_hit(Raindrop(x=0.1, y=1.0, speed=6.5)))   # True:  inside the body
print(p.is_hit(Raindrop(x=0.1, y=2.5, speed=6.5)))   # False: above the head
print(p.is_hit(Raindrop(x=1.0, y=1.0, speed=6.5)))   # False: in front of the person

p.step(0.5)                                          # walks 1 m to the right
print(p.is_hit(Raindrop(x=1.0, y=1.0, speed=6.5))) 