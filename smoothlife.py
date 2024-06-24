"""
Game of life has 4 rules :
    1. A live cell with 1 or no live neighbour dies [underpopulation]
    2. A live cell with 2 or 3 live neighbour lives [survival]
    3. A live cell with 4 or more live neighbour dies [overpopulation]
    4. A dead cell with exactly 3 live neighbours comes to life [reproduction]
"""

# importing libraries
import pygame
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import random
import numpy as np
import raster_geometry

# initialize the pygame module so we can utilize it
pygame.init()
pygame.font.init()

# three colors that we'll be using for the game
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)

WIDTH, HEIGHT = 1280, 720  # height and width of the screen where we'll play the game
TILE_SIZE = 10  # width and height of each individual grid box
GRID_WIDTH = WIDTH // TILE_SIZE  # number of tiles we'll have across the width
GRID_HEIGHT = HEIGHT // TILE_SIZE  # number of tiles we'll have across the height of the screen
FPS = 60  # the while loop runs this many times per second

# now the screen is where we'll be doing all our pygame drawing. This is how we initialize a new pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

slider = Slider(screen, 400, 20, 200, 15, min=4, max=20, step=1)
output = TextBox(screen, 1025, 5, 50, 50, fontSize=30)

clock = pygame.time.Clock()


def gen(num):
    return set([(random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT), np.round(random.random(), 1)) for _ in range(num)])


def draw_grid(positions):  # it takes in a set of positions where there are live cells, so that for checking the rules,
    # we won't have to loop over every cell
    for position in positions:
        col, row, in10ct = position  # our position is indicated by column number and a row number
        top_left = (col * TILE_SIZE, row * TILE_SIZE)  # translating the indexes into pixel positions
        pygame.draw.rect(screen, tuple([in10ct*x for x in YELLOW]), (*top_left, TILE_SIZE, TILE_SIZE))
        # the *top_left indicates that we're unpacking the arguments of the tuple, so instead of taking it as a
        # couple, we're considering writing them as 2 separate arguments

    for row in range(GRID_HEIGHT):  # drawing lines for every single row (going from top to bottom)
        pygame.draw.line(screen, BLACK, (0, row * TILE_SIZE), (WIDTH, row * TILE_SIZE))  # draw a line on the screen,
        # which is black in colour, and then we specify the starting position and the ending position of that line

    for col in range(GRID_WIDTH):  # drawing lines for every single column (from left to right)
        pygame.draw.line(screen, BLACK, (col * TILE_SIZE, 0), (col * TILE_SIZE, HEIGHT))


def adjust_grid(positions):
    all_neighbors = set()
    new_positions = set()

    for position in positions:
        neighbors = get_inner_neighbors(position)
        all_neighbors.update(neighbors)

        neighbors = list(filter(lambda x: x in positions, neighbors))

        intensities = [i[2] for i in neighbors]

        # A live cell with 2 or 3 live neighbour lives[survival]
        if 0.2 <= sum(intensities) <= 0.3:
            new_positions.add(position)

    for position in all_neighbors:
        neighbors = get_inner_neighbors(position)
        neighbors = list(filter(lambda x: x in positions, neighbors))

        intensities = [i[2] for i in neighbors]

        if 0.3 <= sum(intensities) <= 0.35:
            new_positions.add(position)

    return new_positions


def get_inner_neighbors(pos):
    x, y, i = pos
    neighbors = []
    for dx in [_ for _ in [-1, 0, 1]]:
        if x + dx < 0 or x + dx > GRID_WIDTH:
            continue
        for dy in [_ for _ in [-1, 0, 1]]:
            if y + dy < 0 or y + dy > GRID_HEIGHT:
                continue
            if dx == 0 and dy == 0:
                continue

            neighbors.append((x + dx, y + dy, i))

    return neighbors


def main():
    """
    Whenever we're working with pygame we have something called as an event loop or a main loop, and this function is
    supposed to run constantly in the background checking the logic, and the input, and button presses etc.
    This is where most of the core functions will be called from.
    """
    running = True  # running represents whether our game is running or not
    playing = False  # Just determines if YOU'VE paused the game or if it's playing (only to be showed in the title bar)
    count = 0  # for each loop, counts increases
    update_freq = 10  # once the count reaches the update frequency, the game is updated
    # Since our FPS is 60, and our update_frequency is 2, which means game will run on 30 FPS
    iterations = 0  # To count the number of iterations

    positions = set()  # just mentioning that positions is a set of locations where there'll be live cells
    while running:  # this is our main loop
        font = pygame.font.Font(None, 36)
        clock.tick(FPS)  # this regulates the speed of the while loop, so that it only executes that many times in
        # second. It's not a problem in slow computers, but it'll restrict the fast computers where this can go haywire

        if playing:
            count += 1

        if count >= update_freq:
            count = 0
            positions = adjust_grid(positions)
            iterations += 1

        pygame.display.set_caption("Playing" if playing else "Paused")

        # for handling an event where a user wants to quit the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if event.type == pygame.MOUSEBUTTONDOWN:  # if it registers a mouse click
            if pygame.mouse.get_pressed()[0]:  # this argument instead allows the user to click and drag
                x, y = pygame.mouse.get_pos()  # get the positions for the moues click
                col = x // TILE_SIZE  # figuring out the tile position from the mouse coordinates
                row = y // TILE_SIZE
                intensity = 1
                pos = (col, row, intensity)

                # If there's already this position in the set of positions, then it'll remove that positions,
                # else add it
                if pos in positions:
                    positions.remove(pos)
                else:
                    positions.add(pos)

            if event.type == pygame.KEYDOWN:  # in the event that a key is pressed
                if event.key == pygame.K_SPACE:  # if it's a space bar
                    playing = not playing  # reverse the state of playing (if it's tru then false and vice versa)

                if event.key == pygame.K_c:  # if the c key is pressed
                    positions = set()  # the set of positions is emptied out
                    playing = False  # and the game is paused
                    count = 0
                    iterations = 0

                if event.key == pygame.K_g:
                    positions = gen(random.randrange(4, 10) * GRID_WIDTH)

        screen.fill(GREY)  # we're going to fill the screen with GREY color
        draw_grid(positions)  # and then we're going to draw the grid.
        score_text = font.render(f'Iterations: {iterations}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        output.setText(slider.getValue())
        pygame_widgets.update(event)
        pygame.display.update()  # and then we'll update the display
        # The above three commands needs to be in order. If we wrote draw_grid, and then screen.fill, then you'll
        # only see a gray screen because pygame would draw the grid, and then fill the screen with GREY

    pygame.quit()


if __name__ == "__main__":
    #main()
    print(np.round(raster_geometry.circle(20, 9, smoothing=1.0), 2) - np.round(raster_geometry.circle(20, 3, smoothing=0.5), 2))