import numpy as np
import math
import pygame


# classes
class Vector3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class Triangle:
    def __init__(self, vectors=[]):
        self.vectors = vectors


class Mesh:
    def __init__(self):
        self.triangles = []


def draw_triangle(triangle, color=(255, 255, 255)):
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

    pygame.draw.line(screen, color, (x1, y1), (x2, y2))
    pygame.draw.line(screen, color, (x2, y2), (x3, y3))
    pygame.draw.line(screen, color, (x3, y3), (x1, y1))


def project_triangle(triangle):
    new_triangle = Triangle()
    new_triangle.vectors = []
    for v in triangle.vectors:
        m = np.matrix([v.x, v.y, v.z, 1])
        p = np.matmul(m, proj_matrix)
        z = p.item(3)

        if z != 0:
            new_triangle.vectors.append(Vector3(p.item(0) / z, p.item(1) / z, p.item(2) / z))
        else:
            new_triangle.vectors.append(Vector3(p.item(0), p.item(1), p.item(2)))

    return transform(transform(new_triangle, 0), 1)


def transform(triangle, id=1):
    angle = frame / 6000
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


cube = (
    # front
    ((0, 0, 0), (0, 1, 0), (1, 1, 0)),
    ((0, 0, 0), (1, 1, 0), (1, 0, 0)),

    # back
    ((0, 0, 1), (0, 1, 1), (1, 1, 1)),
    ((0, 0, 1), (1, 1, 1), (1, 0, 1)),

    # left
    ((1, 0, 0), (1, 1, 0), (1, 0, 1)),
    ((1, 0, 0), (1, 1, 1), (1, 0, 1)),

    # right
    ((0, 0, 1), (0, 1, 1), (0, 1, 0)),
    ((0, 0, 1), (0, 1, 0), (0, 0, 0)),

    # top
    ((0, 1, 0), (0, 1, 1), (1, 1, 1)),
    ((0, 1, 0), (1, 1, 1), (1, 1, 0)),

    # bot
    ((0, 0, 0), (0, 0, 1), (1, 0, 1)),
    ((0, 0, 0), (1, 0, 1), (1, 0, 0))
)

# Create the cube mesh
mesh = Mesh()
for i in cube:
    v = []
    for j in i:
        v.append(Vector3(j[0], j[1], j[2]))
    mesh.triangles.append(Triangle(v))

# pygame constants
screen = pygame.display.set_mode((1366, 768))
screen_x = screen.get_width()
screen_y = screen.get_height()
clock = pygame.time.Clock()

# constants needed for math
near = 0.1
far = 1000
fov = 90
t_fov = (1 / math.tan(fov / 2))
a_ratio = screen_x / screen_y
q = far / (far - near)
proj_matrix = np.matrix(
    [
        [a_ratio * t_fov, 0, 0, 0],
        [0, t_fov, 0, 0],
        [0, 0, q, 1],
        [0, 0, -near * q, 0]
    ]
)

while True:
    frame = pygame.time.get_ticks()
    screen.fill(0)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()

    for t in mesh.triangles:
        triangle = project_triangle(t)
        draw_triangle(triangle)


    clock.tick(60)
    pygame.display.update()