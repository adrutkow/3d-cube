from random import randint

import numpy as np
import math
import pygame


# classes
class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z


class Triangle:
    def __init__(self, vectors=[]):
        self.vectors = vectors


class Mesh:
    def __init__(self):
        self.triangles = []


class Camera:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0


def draw_triangle(triangle, color=(255, 255, 255)):
    # Draw triangle if its norm has an angle facing the camera
    line1 = Vector3()
    line2 = Vector3()
    norm = Vector3()

    line1.x = triangle.vectors[1].x - triangle.vectors[0].x
    line1.y = triangle.vectors[1].y - triangle.vectors[0].y
    line1.z = triangle.vectors[1].z - triangle.vectors[0].z

    line2.x = triangle.vectors[2].x - triangle.vectors[0].x
    line2.y = triangle.vectors[2].y - triangle.vectors[0].y
    line2.z = triangle.vectors[2].z - triangle.vectors[0].z

    norm.x = line1.y * line2.z - line1.z * line2.y
    norm.y = line1.z * line2.x - line1.x * line2.z
    norm.z = line1.x * line2.y - line1.y * line2.x

    l = math.sqrt(norm.x**2 + norm.y**2 + norm.z**2)
    norm.x /= l
    norm.y /= l
    norm.z /= l

    if not (norm.x * (triangle.vectors[0].x - camera.x) +
            norm.y * (triangle.vectors[0].y - camera.y) +
            norm.z * (triangle.vectors[0].z - camera.z) < 0):
        return

    v1, v2, v3 = triangle.vectors
    x1, y1 = v1.x, v1.y
    x2, y2 = v2.x, v2.y
    x3, y3 = v3.x, v3.y

    # Scale it to view
    x1 += 1
    x2 += 1
    x3 += 1
    y1 += 1
    y2 += 1
    y3 += 1

    x1 *= 0.5 * screen_x
    x2 *= 0.5 * screen_x
    x3 *= 0.5 * screen_x
    y1 *= 0.5 * screen_y
    y2 *= 0.5 * screen_y
    y3 *= 0.5 * screen_y

    light_direction = Vector3(0, 0, -1)
    l = math.sqrt(light_direction.x**2 + light_direction.y**2 + light_direction.z**2)
    light_direction.x /= l
    light_direction.y /= l
    light_direction.z /= l

    dp = norm.x * light_direction.x + norm.y * light_direction.y + norm.z * light_direction.z

    color = [100 + dp*100]*3
    print(color)
    print(dp)
    mesh_color = [0]*3

    # Draw
    pygame.draw.polygon(screen, color, ((x1, y1),(x2, y2),(x3, y3)), width=0)
    pygame.draw.line(screen, mesh_color, (x1, y1), (x2, y2))
    pygame.draw.line(screen, mesh_color, (x2, y2), (x3, y3))
    pygame.draw.line(screen, mesh_color, (x3, y3), (x1, y1))



def project_triangle(triangle):
    new_triangle = Triangle()
    new_triangle.vectors = []
    for v in triangle.vectors:
        m = np.matrix([v.x, v.y, v.z + 2, 1])
        p = np.matmul(m, proj_matrix)

        x = p.item(0)
        y = p.item(1)
        z = p.item(2)
        w = p.item(3)

        if w != 0:
            x /= w
            y /= w
            z /= w

        new_triangle.vectors.append(Vector3(x, y, z))

    return new_triangle

def transform(triangle, id=1):
    angle = frame / 1500
    new_triangle = Triangle()
    new_triangle.vectors = []
    transformations = [
        # X axis rotation
        np.matrix([
                [1, 0, 0, 0],
                [0, math.cos(angle), -math.sin(angle), 0],
                [0, math.sin(angle), math.cos(angle), 0],
                [0, 0, 0, 0]
            ]),
        # Y axis rotation
        np.matrix([
                [math.cos(angle), 0, math.sin(angle), 0],
                [0, 1, 0, 0],
                [-math.sin(angle), 0, math.cos(angle), 0],
                [0, 0, 0, 0]
        ])
    ]

    for v in triangle.vectors:
        m = np.matrix([v.x, v.y, v.z, 1])
        p = np.matmul(m, transformations[id])
        new_triangle.vectors.append(Vector3(p.item(0), p.item(1), p.item(2)))
    return new_triangle


# misc variables
camera = Camera()

# pygame constants
screen = pygame.display.set_mode((800, 800))
screen_x = screen.get_width()
screen_y = screen.get_height()
clock = pygame.time.Clock()

# constants needed for math
near = 0.1
far = 1000
fov = 90
t_fov = (1 / math.tan((fov * 0.5 / 180 * math.pi)))
a_ratio = screen_y / screen_x
q = far / (far - near)
proj_matrix = np.matrix(
    [
        [a_ratio * t_fov, 0,     0,         0],
        [0,               t_fov, 0,         0],
        [0,               0,     q,         1],
        [0,               0,     -near * q, 0]
    ]
)

cube = (
    ((0, 0, 0), (0, 0, 1), (1, 0, 1)),
    ((0, 0, 0), (1, 0, 1), (1, 0, 0)),
    ((0, 0, 1), (0, 1, 1), (1, 1, 1)),
    ((0, 0, 1), (1, 1, 1), (1, 0, 1))
)

cube = (
    # front
    ((0, 0, 0), (0, 1, 0), (1, 1, 0)),
    ((0, 0, 0), (1, 1, 0), (1, 0, 0)),

    # back
    ((1, 0, 1), (1, 1, 1), (0, 1, 1)),
    ((1, 0, 1), (0, 1, 1), (0, 0, 1)),

    # left
    ((1, 0, 0), (1, 1, 0), (1, 1, 1)),
    ((1, 0, 0), (1, 1, 1), (1, 0, 1)),

    # right
    ((0, 0, 1), (0, 1, 1), (0, 1, 0)),
    ((0, 0, 1), (0, 1, 0), (0, 0, 0)),

    # top
    ((0, 1, 0), (0, 1, 1), (1, 1, 1)),
    ((0, 1, 0), (1, 1, 1), (1, 1, 0)),

    # bot
    ((0, 0, 0), (1, 0, 1), (0, 0, 1)),
    ((0, 0, 0), (1, 0, 0), (1, 0, 1))
)

# Create the cube mesh
mesh = Mesh()
for i in cube:
    v = []
    for j in i:
        v.append(Vector3(j[0] * a_ratio, j[1], j[2]))
    mesh.triangles.append(Triangle(v))


while True:
    frame = pygame.time.get_ticks()
    screen.fill(0)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
        keys = pygame.key.get_pressed()
        speed = 10
        if keys[pygame.K_w]:
            camera.z += speed
        if keys[pygame.K_s]:
            camera.z -= speed
        if keys[pygame.K_a]:
            camera.x -= speed
        if keys[pygame.K_d]:
            camera.x += speed

    for t in mesh.triangles:
        triangle = transform(t, 0)
        triangle = transform(triangle, 1)
        triangle = project_triangle(triangle)

        draw_triangle(triangle)

    clock.tick(60)
    pygame.display.update()
