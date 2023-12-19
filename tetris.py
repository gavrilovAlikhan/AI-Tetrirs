# IMPORTS
import pygame
import random
from pynput.keyboard import Key, Controller
import pyautogui
import copy

pyautogui.PAUSE = 0
# creating the data structure for pieces
# setting up global vars
# functions
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape in main
# - setting up the main

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

# Initiate pygame objects
pygame.font.init()
pygame.mixer.init()

# Load sound effects
theme_soundtrack = pygame.mixer.music.load('theme.mp3')
clear_row = pygame.mixer.Sound('clear.mp3')

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

# Coords
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# Lists of shapes and their colors
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape

# Create empty bag that will contain tetromino shapes
bag = []


# Piece object
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


# Create grid
def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]  # intialise black color for each grid position

    # Check for colors
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


# Convert the shape of the piece
def convert_shape_format(shape):
    positions = []  # list of positions
    # get a sublist of the shape depending on its rotation
    format = shape.shape[shape.rotation % len(shape.shape)]

    # iterate through the shape and get positions for each block
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


# Check for valid spaces in the grid
def valid_space(shape, grid):
    # check for black color on a grid and create list of accepted positions
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    # format the shape of a current piece
    formatted = convert_shape_format(shape)

    # check if piece is in an accepted_pos
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


# Check if the game is over
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:  # if piece above the screen
            return True

    return False


###### 7-bag-randomizer #########
def create_bag():
    global bag
    bag = shapes.copy()  # get copy of a shapes list
    random.shuffle(bag)  # rearrange pieces in the bag


def get_next_tetromino():
    global bag
    if not bag:
        create_bag()
    return bag.pop()  # pop the piece from a bag


def update_pieces():
    global current_piece, next_piece
    current_piece = next_piece
    next_piece = get_next_tetromino()


#############################################

# GET TETRIS PIECE WITH RANDOM SHAPE
def get_shape(shape):
    return Piece(5, 0, shape)


# Draw text in the main menu
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (
        top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - (label.get_height() / 2)))


# Draw the tetris grid (lines)
def draw_grid(surface, grid):
    # coordinates
    sx = top_left_x
    sy = top_left_y

    # DRAW LINES FOR A GRID
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))


# Clear full rows
def clear_rows(grid, locked):
    inc = 0
    # iterate through grid from bottom
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        # if ther is block
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    # update the locked positions
    if inc > 0:
        clear_row.play()
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


# Draw the next shape
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    # iterate through shape
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':  # if block
                # draw
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 50))


# Display everything in the game
def draw_window(surface, grid, score=0, rows=0, generation=0, individual_idx=0, condition=True):
    surface.fill((0, 0, 0))  # fill surface in black

    # DRAW TITLE
    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    # PUT TITLE ON MIDDLE OF A SCREEN
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # draw the blocks on a grid (based on color in grid[i][j])
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # DRAW RED BORDERS OF A GRID
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4)

    # DRAW SCORE
    font = pygame.font.SysFont('comicsans', 30)
    font1 = pygame.font.SysFont('comicsans', 18)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))
    label_score = font.render('Lines: ' + str(rows), 1, (255, 255, 255))

    # DRAW MOVEMENT INSTRUCTIONS
    label_movement = font1.render("[Arrow Keys]: Movement", 1, (255, 255, 255))
    label_drop = font1.render("[Space]: Hard Drop", 1, (255, 255, 255))
    label_menu = font1.render("[Escape]: Main Menu", 1, (255, 255, 255))

    # CORDS FOR LABELs
    sx = top_left_x + play_width
    sy = top_left_y + play_height / 2 - 100
    surface.blit(label, (sx + 20, sy + 160))
    surface.blit(label_score, (sx + 20, sy + 190))
    surface.blit(label_movement, (sx - 530, sy + 250))
    surface.blit(label_drop, (sx - 530, sy + 290))
    surface.blit(label_menu, (sx - 530, sy + 330))
    if condition:
        label_generation = font.render('Generation: ' + str(generation), 1, (255, 255, 255))
        label_individual = font.render('Individual: ' + str(individual_idx), 1, (255, 255, 255))
        surface.blit(label_generation, (sx - 530, sy - 200))
        surface.blit(label_individual, (sx - 530, sy - 160))

    draw_grid(surface, grid)
    # pygame.display.update()


# Random Player bot
def random_player():
    movement_list = [Key.up, Key.left, Key.right, Key.down, Key.space]
    button = random.choice(movement_list)
    pressKey(button)


# Get number of holes
def get_holes(grid):
    holes = 0
    overhead = 0
    # Iterate through grid
    for i in range(10):
        found_cell = False
        over_in_row = 0
        for j in range(20):
            if grid[j][i] != (0, 0, 0):
                found_cell = True  # If found cell which is not empty
                over_in_row += 1
            if found_cell and grid[j][i] == (0, 0, 0):  # If found cell and holes increase num of holes
                holes += 1
                overhead += over_in_row
    return holes


# Get bumpiness
def calculateBumpiness(grid):
    bumpiness = 0

    # Get column height
    def col_height(col):
        for row in range(len(grid)):
            if grid[row][col] != (0, 0, 0):
                return len(grid) - row
        return 0

    # Calculate the absolute difference
    for col in range(len(grid[0]) - 1):
        left_height = col_height(col)
        right_height = col_height(col + 1)
        bumpiness += abs(left_height - right_height)

    return bumpiness


# Get clearing piece
def clearing_piece(grid):
    inc = 0
    # Search for full row in the grid
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
    return inc


################################################
############### AI AGENT #######################
################################################

has_executed = False  # control parameter for agent initialisation


def agent(piece, grid, w1, w2, w3, w4):
    global has_executed
    if not has_executed:
        main_dict = {}  # dict with ratings
        for j in range(len(piece.shape)):  # iterate through rotations
            grid_copy = copy.deepcopy(grid)  # create copy of grid
            piece.rotation = j  # set the rotation
            piece_pos = convert_shape_format(piece)  # get piece blocks coords
            x0, y0 = piece_pos[0]
            x1, y1 = piece_pos[1]
            x2, y2 = piece_pos[2]
            x3, y3 = piece_pos[3]

            xb0, xb1, xb2, xb3, yb0, yb1, yb2, yb3 = x0, x1, x2, x3, y0, y1, y2, y3  # save the values

            # max y = 19 max x = 9
            # todo:
            #  BEFORE STARTING SAVE THE INITIAL ROTATION (piece.rotation)
            #  1) find min x
            #  2) see by how much change all x's if changing "min x" value to 0
            #  3) start to change y till Y MIN = 19 or piece present (not (0,0,0) )
            #  4) calculate the height
            #  5) when checked and calculated, do the same with x = 1,2,3... and continue till X MAX = 9
            #  6) when the optimal solution is found, calculate the moves
            #  (e.g if X initial = 5, X optimal = 3 => go left 2 times => drop)

            x_min = min(x0, x1, x2, x3)
            x_max = max(x0, x1, x2, x3)
            y_min = max(y0, y1, y2, y3)
            xb_min, xb_max, yb_min = x_min, x_max, y_min
            height_moves = {}

            # move piece to the left
            while x_min != 0:
                x_min -= 1
                x0 -= 1
                x1 -= 1
                x2 -= 1
                x3 -= 1

            x0_left, x1_left, x2_left, x3_left = x0, x1, x2, x3
            x_max = max(x0, x1, x2, x3)

            # start moving the piece to the right
            for i in range(10):
                x0, x1, x2, x3 = x0_left, x1_left, x2_left, x3_left
                # y0, y1, y2, y3 = yb0, yb1, yb2, yb3
                x_max += i
                x0 += i
                x1 += i
                x2 += i
                x3 += i

                x_max = max(x0, x1, x2, x3)
                if x_max > 9:
                    continue
                # start dropping the piece
                while y_min != 19:
                    y_min += 1
                    y0 += 1
                    y1 += 1
                    y2 += 1
                    y3 += 1
                    if grid[y0][x0] != (0, 0, 0) or grid[y1][x1] != (0, 0, 0) or grid[y2][x2] != (0, 0, 0) or grid[y3][
                        x3] != (
                            0, 0, 0):
                        y_min -= 1
                        y0 -= 1
                        y1 -= 1
                        y2 -= 1
                        y3 -= 1
                        break
                # get coords
                check_coords = [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
                grid_test = copy.deepcopy(grid)  # create copy of a grid
                grid_test[y0][x0], grid_test[y1][x1], grid_test[y2][x2], grid_test[y3][x3] = (1, 1, 1), (1, 1, 1), (
                    1, 1, 1), (1, 1, 1)  # fill the copied grid
                # todo: create a copy of a grid, and put these cords in a copy

                rating = w1 * min(check_coords, key=lambda x: x[1])[1] + w2 * get_holes(
                    grid_test) + w3 * calculateBumpiness(grid_test) + w4 * clearing_piece(grid_test)  # calculate rating

                height_moves[i] = rating  # save position rating

                # reset values
                x_min, x_max, y_min = xb_min, xb_max, yb_min
                x0, x1, x2, x3, y0, y1, y2, y3 = xb0, xb1, xb2, xb3, yb0, yb1, yb2, yb3

                main_dict[j] = height_moves  # save position rating with rotation
                grid_test = grid_copy

        # Get rotation and coordinates of the best rating positon
        global max_height, go_coord, main_rotation
        max_height = -1000
        go_coord = None
        main_rotation = None

        for rotation, positions in main_dict.items():
            for coord, height in positions.items():
                if height > max_height:
                    max_height = height
                    go_coord = coord
                    main_rotation = rotation

        has_executed = True # set that the agent was executed

################################################################

# Movement of an Agent
def movement(tetromino, rotation, x, coord):
    tetromino.rotation = rotation
    if x < coord:
        pressK("right")
    elif x > coord:
        pressK("left")
    else:
        pressK("down")

# KEY SIMULATIONS #
keyboard = Controller()

def pressKey(button):
    # time.sleep(1)
    keyboard.press(button)
    keyboard.release(button)


def pressK(button):
    pyautogui.press(button)

#################################




################ GENETIC ALGORITHMS ###############################

# Global variables
population_size = 50
num_gnerations = 30
mutation_rate = 0.1

# Create individual with random weights
def create_individual():
    return [random.uniform(-10, 10) for _ in range(4)]

# Create first generation
def create_initial_population():
    return [create_individual() for _ in range(population_size)]

# Calculate the fitness
def fitness(individual, generation, individual_idx):
    print("Generation:", generation, 'Individual:', individual_idx, "Chromosome:", individual)
    return main(win, individual, generation, individual_idx, True)

# Selection operator
def selection(population, fitnesses):
    # Tournament selection
    tournament_size = 5
    parents = []
    for _ in range(2):  # Select 2 parents
        competitors = random.sample(list(zip(population, fitnesses)), tournament_size)
        winner = max(competitors, key=lambda x: x[1])
        parents.append(winner[0])
    return parents

# Mutation operator
def mutate(individual, mutation_rate):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            individual[i] += random.uniform(-0.1, 0.1)

# Crossover operator
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

############################### DATA GATHERING #####################################
def save_population(population, generation):
    filename = f"population_generation_{generation}.txt"

    with open(filename, "w") as f:
        for individual in population:
            weights_str = " ".join(map(str, individual))
            f.write(f"{weights_str}\n")


def save_fitnesses(fitnesses, generation):
    filename = f"fitnesses_generation_{generation}.txt"

    with open(filename, "w") as f:
        for fitness in fitnesses:
            f.write(f"{fitness}\n")


def save_best_individual(individual, generation):
    filename = f"best_individual_generation_{generation}.txt"

    with open(filename, "w") as f:
        weights = individual[0]  # Extract weights from the tuple (weights, fitness)
        weights_str = " ".join(map(str, weights))
        f.write(f"{weights_str}\n")


def load_population(filename):
    population = []

    with open(filename, "r") as f:
        for line in f:
            weights_str = line.strip().split()
            individual = [float(w) for w in weights_str]
            population.append(individual)

    return population
#####################################################################



create_bag() # initalise the bag of tetromino pieces
def main(win, individual, generation, ind_idx, choice=True): # Choice for the game option (if TRUE: GAs and Trained AI, else just normal Tetris)

    # Initial variables
    locked_positions = {}
    grid = create_grid(locked_positions)
    global has_executed
    change_piece = False
    has_executed = False
    run = True
    # Get pieces from the bag
    current_piece = get_shape(get_next_tetromino())
    next_piece = get_shape(get_next_tetromino())

    # Set time, music and initial scores
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.37
    level_time = 0
    rows = 0
    score = 0
    moves = 0
    clear_lines = 0
    pygame.mixer.music.play(-1)

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase game speed every 5 seconds
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if choice:
            value = 0.01
        else:
            value = fall_speed

        # Drop piece from top
        if fall_time / 1000 >= value:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Check for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # go to main menu
                    run = False
                    pygame.mixer.music.stop()
                    main_menu(win)
                # MOVEMENT
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                if event.key == pygame.K_SPACE:
                    while True:
                        current_piece.y += 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.y -= 1
                            break

        ############ INITIATE AGENT ##################################################

        # Get piece coordinates
        pos = convert_shape_format(current_piece)
        x1, x2, x3, x4 = pos[0][0], pos[1][0], pos[2][0], pos[3][0]
        x_min = min(x1, x2, x3, x4)

        # Run agent
        if choice:
            if current_piece.y > 2:
                agent(current_piece, grid, individual[0], individual[1], individual[2], individual[3])
                movement(current_piece, main_rotation, x_min, go_coord)

        ###############################################################################

        shape_pos = convert_shape_format(current_piece)

        # Fill grid with colors according to the piece coordinate
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # Give next piece
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape(get_next_tetromino())
            change_piece = False
            has_executed = False

            # Set score
            moves += 1
            rows = clear_rows(grid, locked_positions)
            clear_lines += rows
            if rows == 1:
                score += 40
            elif rows == 2:
                score += 100
            elif rows == 3:
                score += 300
            elif rows == 4:
                score += 1200
            else:
                score == 0

        # Draw everything
        draw_window(win, grid, score, clear_lines, generation, ind_idx, choice)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check for the game over
        if choice:
            if check_lost(locked_positions):
                draw_text_middle(win, "You Lost!", 80, (255, 255, 255))
                pygame.mixer.music.stop()
                pygame.display.update()
                pygame.time.delay(1500)
                if clear_lines == 0:
                    return 0
                else:
                    return clear_lines
                run = False
                # main(win)
        else:
            if check_lost(locked_positions):
                draw_text_middle(win, "You Lost!", 80, (255, 255, 255))
                pygame.mixer.music.stop()
                pygame.display.update()
                pygame.time.delay(1500)
                run = False

# MAIN MENU

def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press [1] Tetris [2] Trained AI [3] GAs Process', 30, (255, 255, 255))
        pygame.display.update()
        # THREE OPTIONS
        for event in pygame.event.get():
            # IF QUIT
            if event.type == pygame.QUIT:
                run = False
                pygame.mixer.music.stop()
            if event.type == pygame.KEYDOWN:
                # Normal Tetris
                if event.key == pygame.K_1:
                    main(win, None, None, None, False)
                # Trained Agent
                if event.key == pygame.K_2:
                    player = [0.5436822764440379, -9.328911430903139, -1.735608284805026, 6.577302970502618]
                    main(win, player, 13, 1, True)
                # Genetic Algorithms
                if event.key == pygame.K_3:
                    population = create_initial_population() # create first generation
                    # save_population(population, 0)
                    # iterate through number of generations
                    for generation in range(num_gnerations):
                        # get fitness scores
                        fitnesses = [fitness(individual, generation, i) for i, individual in enumerate(population)]
                        # save_fitnesses(fitnesses, generation)

                        # get best individual in a generation
                        best_individual = max(zip(population, fitnesses), key=lambda x: x[1])
                        # save_best_individual(best_individual, generation)

                        # Print best individual
                        print(
                            f"Generation {generation}: Best fitness = {best_individual[1]}, Weights = {best_individual[0]}")

                        # Create new population
                        new_population = []

                        # Perform evolution
                        while len(new_population) < population_size:
                            # Selection
                            parent1, parent2 = selection(population, fitnesses)

                            # Crossover
                            offspring1, offspring2 = crossover(parent1, parent2)

                            # Mutation
                            mutate(offspring1, mutation_rate)
                            mutate(offspring2, mutation_rate)

                            new_population.extend([offspring1, offspring2])
                        population = new_population
                        # save_population(population, generation)

    pygame.display.quit()

# Surfaces
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Tetris")
main_menu(win)  # start game
