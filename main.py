import pygame
import math
import glm
from glm import vec3

class Ray():
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = glm.normalize(direction)
    
    def at(self, t):
        return self.origin + t*self.direction

class Camera():
    def __init__(self, center, euler_angles, width, height, focal_length):
        self.center = center
        self.width  = width
        self.height = height
        self.focal_length = focal_length
        euler_angles = glm.radians(euler_angles)
        matrix = glm.mat4()
        matrix = glm.rotate(matrix, euler_angles.x, vec3(1, 0, 0))
        matrix = glm.rotate(matrix, euler_angles.y, vec3(0, 1, 0))
        matrix = glm.rotate(matrix, euler_angles.z, vec3(0, 0, 1))
        self.right  = glm.vec4(1, 0, 0, 1) * matrix
        self.up     = glm.vec4(0, 1, 0, 1) * matrix
        self.front  = glm.vec4(0, 0, 1, 1) * matrix

    def get_ray(self, j, i):
        direction  = self.front * self.focal_length
        direction += self.right*(j/self.width - 0.5)
        direction += self.up*(self.height/self.width)*(i/self.height - 0.5)
        return Ray(self.center, vec3(direction))

class Hit():
    def __init__(self, object, position, normal, distance):
        self.object   = object
        self.position = position
        self.normal   = normal
        self.distance = distance

class Sphere():
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color  = color
    
    def intersect(self, ray):
        a = glm.dot(ray.direction, ray.direction)
        s0_p0 = ray.origin - self.center
        b = 2.0*glm.dot(ray.direction, s0_p0)
        c = glm.dot(s0_p0, s0_p0) - self.radius**2
        delta = b**2 - 4.0*a*c
        if(delta > 0):
            sqrt_delta = math.sqrt(delta)
            bhaskara = lambda d: (-b + d)/(2.0*a)
            solutions = [bhaskara(sqrt_delta), bhaskara(-sqrt_delta)]
            positive_solutions = [s for s in solutions if s > 0]
            if(len(positive_solutions) > 0):
                distance = min(positive_solutions)
                hit_point = ray.at(distance)
                normal = glm.normalize(hit_point - self.center)
                return Hit(self, hit_point, normal, distance)
        return None

class PointLight():
    def __init__(self, position, intensity):
        self.position  = position
        self.intensity = intensity
    
    def intensity_at(self, hit):
        direction = self.position - hit.position 
        distance  = glm.length(direction)
        direction = glm.normalize(direction)
        cos_theta = glm.dot(direction, hit.normal)
        return max(0, self.intensity*cos_theta/distance**2)

class Scene():
    def __init__(self, background, ambient_light):
        self.background = background
        self.ambient_light = ambient_light
        self.objects = []
        self.lights  = []

    def closest(self, ray):
        closest_hit = None
        for object in self.objects:
            hit = object.intersect(ray)
            if hit and (not closest_hit or hit.distance < closest_hit.distance):
                closest_hit = hit
        return closest_hit
    
    def trace(self, ray):
        closest_hit = self.closest(ray)
        if closest_hit:
            intensity = self.ambient_light
            for light in self.lights:
                light_ray = Ray(light.position, closest_hit.position - light.position)
                light_hit = self.closest(light_ray)
                if(light_hit and light_hit.object == closest_hit.object):
                    intensity += light.intensity_at(closest_hit)
            return closest_hit.object.color*min(intensity, 1)
        else:
            return self.background

def render(scene, camera):
    surface = pygame.display.set_mode((camera.width, camera.height))
    surface.fill((125, 125, 125))
    i = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        if i < camera.height: 
            for j in range(0, camera.width):
                pixel_center = (j + 0.5, camera.height - 0.5 - i)
                color = scene.trace(camera.get_ray(*pixel_center)) 
                surface.set_at((j, i), color)
            pygame.display.flip()
            i += 1

if __name__=="__main__":
    scene = Scene(vec3(26, 27, 33), 0.12)
    camera = Camera(vec3(0, 5, -8), vec3(-10, 5, 0), 800, 600, 0.7)

    light = PointLight(vec3(-1.3, 8.4, 0), 20)
    scene.lights.append(light)

    sphere1 = Sphere(vec3(2.5, 2.8, 5.15), 2.8, vec3(83, 221, 108))
    scene.objects.append(sphere1)

    sphere2 = Sphere(vec3(0.6, 5.6, 3.6), 0.6, vec3(128, 117, 255))
    scene.objects.append(sphere2)

    sphere3 = Sphere(vec3(-3.1, 1.4, 0.06), 1.4, vec3(128, 117, 255))
    scene.objects.append(sphere3)

    sphere4 = Sphere(vec3(-4.2, 5.4, 4.2), 0.9, vec3(83, 221, 108))
    scene.objects.append(sphere4)

    sphere5 = Sphere(vec3(0, -1000000, 0), 1000000, vec3(234, 234, 234))
    scene.objects.append(sphere5)

    render(scene, camera)