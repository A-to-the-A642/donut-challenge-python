import os
from math import cos, sin
import pygame
import colorsys

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
hue = 0  # starting hue for coloring the torus

# setup for pygame
os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the pygame window on screen
RES = WIDTH, HEIGHT = 800, 800  # screen resolution
FPS = 60  # frames per second

# needs pixel grid
pixel_width = 20  # width of each "character cell"
pixel_height = 20  # height of each "character cell"

x_pixel = 0
y_pixel = 0

# number of "cells" that fit in the screen
screen_width = WIDTH // pixel_width
screen_height = HEIGHT // pixel_height
screen_size = screen_width * screen_height  # total number of cells

# variables for rotation
A, B = 0, 0  # rotation angles for the torus

theta_spacing = 10  # step for the smaller circle of the torus
phi_spacing = 3     # step for the larger circle of the torus

chars = ".,-~:;=!*#$@"  # chars for design of donut

# parameters
R1 = 10  # radius of the tube (small circle)
R2 = 20  # radius from center of tube to center of torus
K2 = 200  # distance from viewer to torus (depth scaling)
K1 = screen_height * K2 * 3 / (8 * (R1 + R2))  # scale factor for projection

# pygame init
pygame.init()
screen = pygame.display.set_mode(RES)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20, bold=True)  # font for drawing characters


def hsv2rgb(h, s, v):
    """
    Converts HSV color to RGB.
    h: hue (0 to 1)
    s: saturation (0 to 1)
    v: value/brightness (0 to 1)
    returns: tuple of (R, G, B)
    """
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def text_display(char, x, y):
    """
    Draw a character on the screen at a given pixel location.
    """
    text = font.render(str(char), True, hsv2rgb(hue, 1, 1))  # color changes with hue
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)


# loop variables
k = 0  # index for the output array
paused = False
running = True


while running:
    clock.tick(FPS)
    pygame.display.set_caption("FPS: {:.2f}".format(clock.get_fps()))
    screen.fill(BLACK)  # clear screen

    # -------------------- BUFFERS --------------------
    output = [' '] * screen_size  # stores character for each cell
    zbuffer = [0] * screen_size   # stores depth for each cell (for occlusion)

    # -------------------- TORUS ROTATION & PROJECTION --------------------
    for theta in range(0, 628, theta_spacing):  # small circle (tube)
        for phi in range(0, 628, phi_spacing):  # large circle (around center)

            # sine cosine for speed
            cosA = cos(A)
            sinA = sin(A)
            cosB = cos(B)
            sinB = sin(B)
            costheta = cos(theta)
            sintheta = sin(theta)
            cosphi = cos(phi)
            sinphi = sin(phi)

            # circle coordinates before rotation
            circlex = R2 + R1 * costheta
            circley = R1 * sintheta

            # 3D coordinates after rotation
            x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
            y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
            z = K2 + cosA * circlex * sinphi + circley * sinA
            ooz = 1 / z  # "one over z" for perspective projection

            # project 3D coordinates to 2D screen coordinates
            xp = int(screen_width / 2 + K1 * ooz * x)
            yp = int(screen_height / 2 - K1 * ooz * y)
            position = xp + screen_width * yp  # linear index for 1D array

            # luminance calculation
            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)

            # update buffers if this point is closer
            if ooz > zbuffer[position]:
                zbuffer[position] = ooz  # update depth
                luminance_index = int(L * 8)
                output[position] = chars[luminance_index if luminance_index > 0 else 0]  # choose character

    # draw to screen
    for i in range(screen_height):
        y_pixel += pixel_height
        for j in range(screen_width):
            x_pixel += pixel_width
            text_display(output[k], x_pixel, y_pixel)
            k += 1
        x_pixel = 0
    y_pixel = 0
    k = 0

    # animation of rotations
    A += 0.15
    B += 0.035
    hue += 0.005  # slowly change color

    if not paused:
        pygame.display.update()

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                paused = not paused
