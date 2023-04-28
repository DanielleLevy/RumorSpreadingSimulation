import sys
import tkinter as tk
import random
import pygame
import numpy as np
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
import csv
import os

# Define the colors to use in the simulation
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN=(0,128,0)
PINK=(250,218,221)
RED=(255, 0, 0)
BLUE=(108, 79, 250)
YELLOW=(245,206,50)
# Define the size of the grid and the window
GRID_SIZE = 100
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
# Set default parameter values
default_p = 0.6
default_s4 = 25
default_s3 = 20
default_s2 = 30
default_s1 = 25
default_l = 7
default_num_generations = 50
default_numofruns=10

#for the plot
count_has_r=0
global count_by_gen


# Define the levels of skepticism
SKEPTICISM_LEVELS = {
    's1': 0,
    's2': 1,
    's3': 2,
    's4': 3
}
# Define the probs for the levels of skepticism
SKEPTICISM_LEVELS_P = {
    's1': 1,
    's2': 1/3,
    's3': 2/3,
    's4': 0
}

#convert the SKEPTICISM_LEVELS dictionary
SKEPTICISM_LEVELS_REVERSED = {v: k for k, v in SKEPTICISM_LEVELS.items()}

class Simulation:
    def __init__(self, p_people, p_skepticism,gen,L):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the instance of the class, and defines what will be stored in that instance.
    In this case, we are storing a grid (a 2D array) of people objects.

    :param self: Represent the instance of the class
    :param p_people: Determine the number of people in the grid
    :param p_skepticism: Determine the percentage of people who are skeptical
    :param gen: Determine the generation of the simulation
    :param L: Set the number of people that are infected at the start
    :return: The grid, which is a 2d array of people
    """
        self.count_by_gen_per = None
        self.p_people = p_people
        self.p_skepticism = p_skepticism
        self.generation=gen
        self.generation_progress=0
        self.l=L
        value_list = list(SKEPTICISM_LEVELS.values())
        value_list += [None]
        self.grid = np.full((GRID_SIZE, GRID_SIZE), None)
        self.num_people = int(p_people * (GRID_SIZE * GRID_SIZE))
        skepticism_levels = []
        for i, percent in enumerate(p_skepticism):
            num_people_s = int(percent * self.num_people)
            skepticism_level = [SKEPTICISM_LEVELS[f"s{len(p_skepticism) - i}"]] * num_people_s
            skepticism_levels += skepticism_level
        np.random.shuffle(skepticism_levels)
        for i in range(self.num_people):
            x, y = np.random.randint(GRID_SIZE), np.random.randint(GRID_SIZE)
            while self.grid[x][y] is not None:
                x, y = np.random.randint(GRID_SIZE), np.random.randint(GRID_SIZE)
            skepticism_level = skepticism_levels[i]
            person = Person(SKEPTICISM_LEVELS_REVERSED.get(skepticism_level))
            self.grid[x][y] = person

    def get_neighbors(self,x,y):
        """
    The get_neighbors function takes in a cell's x and y coordinates,
    and returns the neighbors of that cell.  The neighbors are returned as a list of tuples,
    where each tuple is an (x,y) coordinate pair.

    :param self: Allow an object to refer to itself inside of a method
    :param x: Get the row of the cell
    :param y: Determine the row of the cell, and x is used to determine the column
    :return: A list of tuples
    """
        neighbors=[]
        neighbors_row = range((x - 1), (x + 2))
        neighbors_col = range((y - 1), (y + 2))
        for nr in neighbors_row:
            for nc in neighbors_col:
                nr = nr % GRID_SIZE  # WRAP AROUND
                nc = nc % GRID_SIZE  # WRAP AROUND
                if (nr, nc) != (x, y):
                    neighbors.append((nr, nc))
        return neighbors

    def get_numOfNone(self,x,y):
        """
    The get_numOfNone function takes in the x and y coordinates of a cell,
    and returns the number of neighbors that are None. It does this by first creating two lists,
    neighbors_row and neighbors_col. These lists contain all possible row and column values for a given cell's neighbor.
    For example, if we were looking at (0,0), then its neighbors would be (-2,-2),(-2,-3)...(0,-3)....(2,-3).
    The function then loops through each value in these two lists to find out how many cells are None.

    :param self: Access the attributes of the class
    :param x: Get the x coordinate of a cell in the grid
    :param y: Determine the row of the cell
    :return: The number of none values neighbors in the grid
    """
        mone_none=0
        neighbors_row = range((x - 1), (x + 2))
        neighbors_col = range((y - 1), (y + 2))
        for nr in neighbors_row:
            for nc in neighbors_col:
                nr = nr % GRID_SIZE  # WRAP AROUND
                nc = nc % GRID_SIZE  # WRAP AROUND
                if (nr, nc) != (x, y):
                    if self.grid[nr][nc]==None:
                        mone_none+=1
        return mone_none

    def arrange_board_slow(self):
        """
    The arrange_board_slow function is used to arrange the board in a way that will allow for the most efficient spread of information.
        The function first creates two lists, one containing all of the coordinates on the grid and another containing how many neighbors each coordinate has.
        It then sorts both lists by number of neighbors, so that they are in order from least to greatest number of neighbors.
        Finally, it iterates through these sorted lists and assigns people with different levels of skepticism to each coordinate.

    :param self: Access the attributes of the class
    :return: A list of coordinates, sorted by the number of neighbors that are none
    """
        listOfFree=[]
        moneOfNone=[]
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if self.grid[x][y]!=None:
                    listOfFree.append((x,y))
                    moneOfNone.append(self.get_numOfNone(x,y))

        sorted_coordinates = [listOfFree[i] for i in sorted(range(len(listOfFree)), key=lambda x: moneOfNone[x])]
        i=0;
        for j in range(int(self.p_skepticism[0]*self.num_people)):
            self.grid[sorted_coordinates[i]]=Person('s4')
            i+=1;
        for j in range(int(self.p_skepticism[1]*self.num_people)):
            self.grid[sorted_coordinates[i]]=Person('s3')
            i+=1;
        for j in range(int(self.p_skepticism[2] * self.num_people)):
            self.grid[sorted_coordinates[i]] = Person('s2')
            i += 1;
        for j in range(int(self.p_skepticism[3] * self.num_people)):
            self.grid[sorted_coordinates[i]] = Person('s1')
            i += 1;
    def arrange_board_fast(self):
        """
    The arrange_board_fast function is a function that arranges the board in a way that will minimize the number of interactions between people.
    It does this by first creating two lists, one with all coordinates and one with how many neighbors each coordinate has. Then it sorts both lists based on
    the second list so that they are in order from least to most neighbors. Finally, it goes through and places people at each coordinate starting from the
    coordinate with fewest neighbors.

    :param self: Refer to the object itself
    :return: A list of tuples
    """
        listOfFree=[]
        moneOfNone=[]
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if self.grid[x][y]!=None:
                    listOfFree.append((x,y))
                    moneOfNone.append(self.get_numOfNone(x,y))

        sorted_coordinates = [listOfFree[i] for i in sorted(range(len(listOfFree)), key=lambda x: moneOfNone[x])]
        i=0;
        for j in range(int(self.p_skepticism[3]*self.num_people)):
            self.grid[sorted_coordinates[i]]=Person('s1')
            i+=1;
        for j in range(int(self.p_skepticism[2]*self.num_people)):
            self.grid[sorted_coordinates[i]]=Person('s2')
            i+=1;
        for j in range(int(self.p_skepticism[1] * self.num_people)):
            self.grid[sorted_coordinates[i]] = Person('s3')
            i += 1;
        for j in range(int(self.p_skepticism[0] * self.num_people)):
            self.grid[sorted_coordinates[i]] = Person('s4')
            i += 1;

    def drawGrid(self):
        """
    The drawGrid function draws the grid of cells on the screen.
    It takes no arguments and returns nothing. It uses a nested for loop to iterate through each cell in the grid,
    and then determines what color to draw that cell based on its state.

    :param self: Refer to the object itself
    :return: Nothing
    """
        blockSize = int(WINDOW_WIDTH / GRID_SIZE)
        for x in range(0, WINDOW_WIDTH, blockSize):
            for y in range(40, WINDOW_HEIGHT+40, blockSize):
                # Determine the color to use for this cell
                rect = pygame.Rect(x, y, blockSize, blockSize)
                if self.grid[int(x / blockSize)][int(y / blockSize)-5] is None:
                    pygame.draw.rect(SCREEN, BLACK, rect, 0)
                #elif self.grid[int(x / blockSize)][int(y / blockSize)-5].skepticism=='s4':
                    #pygame.draw.rect(SCREEN, RED, rect, 0)
                #elif self.grid[int(x / blockSize)][int(y / blockSize) - 5].skepticism == 's3':
                    #pygame.draw.rect(SCREEN, BLUE, rect, 0)
                #elif self.grid[int(x / blockSize)][int(y / blockSize)-5].skepticism=='s2':
                    #pygame.draw.rect(SCREEN, YELLOW, rect, 0)
                elif self.grid[int(x / blockSize)][int(y / blockSize)-5].received_rumor:
                    pygame.draw.rect(SCREEN, GREEN, rect, 0)
                else:
                    pygame.draw.rect(SCREEN, WHITE, rect, 0)

    def select_random_cell(self):
        """
    The select_random_cell function is used to select a random cell from the grid.
    It does this by creating two variables, x and y, which are assigned random integers between 0 and GRID_SIZE - 1.
    The function then checks if the cell at that location is empty (None). If it isn't, it will continue to loop until an empty cell is found.

    :param self: Represent the instance of the class
    :return: A random cell in the grid
    """
        cell = None
        while cell is None:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            cell=self.grid[x][y]
        return x,y

    def transmit_rumor(self, x, y,flagisfirst=0):
        """
    The transmit_rumor function is responsible for transmitting the rumor to a cell's neighbors.
    It takes in two parameters: x and y, which are the coordinates of the cell that will transmit
    the rumor. It then checks if this cell has received a rumor (if it hasn't, there's no point in
    transmitting one). If it has received a rumor, we check each of its neighbors to see if they have
    received rumors as well. If they haven't, we generate a random number between 0 and 1; if this number is less than or equal to SKEPTICISM_LEVELS_P[cell.

    :param self: Access the attributes of the class
    :param x: Indicate the x coordinate of the cell
    :param y: Indicate the y coordinate of the cell in which we want to transmit rumor
    :param flagisfirst: Transmit the rumor to all neighbors of the first cell that receives it
    :return: A boolean value, if the rumor is transmitted or not
    """
        global count_has_r
        cell = self.grid[x][y]
        neighbors=self.get_neighbors(x,y)
        if cell.approve_to_transmit:
           for idx in neighbors:
            nr, nc= idx
            if  self.grid[nr][nc] is not None :
                        neighbor = self.grid[nr][nc]
                        transmission_prob = SKEPTICISM_LEVELS_P[cell.skepticism]
                        if flagisfirst==1:
                            #if this s the first cell, we want him to transmit the rumor even if it s4. so we change the transmission_prob to 2 that is alwayas bigger than np.random.uniform(0, 1).
                            transmission_prob=2
                        if np.random.uniform(0, 1) <= transmission_prob:
                            if neighbor.received_rumor and self.generation_progress==neighbor.generation_received:
                                neighbor.decrease_skepticism_level()
                            cell.transmit_rumor(self.l)
                            if  neighbor.received_rumor ==False:
                                #check if the neighbor receveid the roumer in first time and if yes rasid the counter
                                count_has_r +=1
                            neighbor.receive_rumor(self.generation_progress)


    def update_Cell(self):
        """
    The update_Cell function is used to update the cell's life and skepticism level.
    The function first loops through all of the cells in the grid, then checks if a cell exists at that location.
    If it does exist, it will decrease its life by 1 if he transmits a rumor and increase its skepticism level by 1 if it decreased in former gen.

    :param self: Refer to the object itself
    :return: Nothing
    """
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell=self.grid[x][y]
                if cell is not None:
                    cell.decease_L()
                    cell.up_skepticism_level()

    def show_params(self, screen):
        """
    The show_params function is used to display the simulation parameters on the screen.
    It takes in a screen object as an argument and displays text on it using pygame's font module.
    The text displayed includes:
        - The number of people in the simulation (P)
        - The percentage of skeptics at each level (S4%, S3%, S2% and S2%)
        - The value for l, which is a parameter that determines how much influence one person has over another's opinion
    and also it displayed the Generation countdown
    :param self: Access the attributes of the class
    :param screen: Display the text on the screen
    :return: The simulation parameters and the generation countdown
    """
        font = pygame.font.SysFont('Arial', 15)
        parameters_txt = font.render(
        f'Simulation params: P={self.p_people}, S4%={self.p_skepticism[0]*100}, S3%={self.p_skepticism[1]*100}, S2%={self.p_skepticism[2]*100}, S1%={self.p_skepticism[3]*100}, L={self.l}',
        True, BLACK)
        generation_txt = font.render(f'Generation : {self.generation_progress}', True, BLACK)
        count_r = font.render(f'has rumor : {count_has_r}', True, BLACK)

        screen.blit(parameters_txt, (10, 0))
        screen.blit(generation_txt, (10, 20))
        screen.blit(count_r, (400, 20))

    def reset_grid(self):
        """
    The reset_grid function is used to reset the grid.
    It does this by iterating through each cell in the grid and calling its reset function.

    :param self: Represent the instance of the class
    :return: Nothing
    """
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell=self.grid[x][y]
                if cell is not None:
                    cell.reset()

    def run_simulation(self,numruns=1):
        """
           The run_simulation function runs the simulation for a given number of generations.
               It also plots the percentage of people who received the rumor per generation, and saves this data to a CSV file.

           :param self: Refer to the object itself
           :param numruns: Run the simulation multiple times and then average the results
           :return: A plot of the percentage of people who received the news
           """
        #self.arrange_board_fast()
        #self.arrange_board_slow()
        self.count_by_gen_per = [[0] * (self.generation + 1) for _ in range(numruns)]
        for n in range (numruns):
            global SCREEN, CLOCK, count_has_r
            self.reset_grid()
            self.generation_progress=0
            count_has_r=0
            pygame.init()
            CLOCK = pygame.time.Clock()
            SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + 40))
            pygame.display.set_caption("Rumor Spreading Simulation")
            x, y = self.select_random_cell()
            self.grid[x][y].receive_rumor(self.generation_progress)
            count_has_r += 1
            self.count_by_gen_per[n][self.generation_progress]=count_has_r/self.num_people*100
            self.generation_progress += 1
            self.transmit_rumor(x, y,1)
            # main simulation loop
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                SCREEN.fill(PINK)
                self.drawGrid()
                self.show_params(SCREEN)
                pygame.display.update()
                self.update_Cell()
                self.count_by_gen_per[n][self.generation_progress]=count_has_r/self.num_people*100
                self.generation_progress += 1
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        cell = self.grid[i][j]
                        if cell is not None:
                            if cell.received_rumor == True:
                                self.transmit_rumor(i, j)

                if self.generation+1 == self.generation_progress:
                    running = False
                # limit the simulation speed to 10 frames per second
                CLOCK.tick(10)
            # close pygame window and exit
            pygame.quit()

        # compute the average count by generation
        average_count_by_gen = [0] * (self.generation + 1)
        for gen in range(self.generation + 1):
            gen_count_sum = sum([self.count_by_gen_per[n][gen] for n in range(numruns)])
            average_count_by_gen[gen] = gen_count_sum / numruns
        params_str = f'Simulation params: P={self.p_people}, S4%={self.p_skepticism[0] * 100}, S3%={self.p_skepticism[1] * 100}, S2%={self.p_skepticism[2] * 100}, S1%={self.p_skepticism[3] * 100}, L={self.l}'
        # save the data to a CSV file
        filename = 'average_count_by_gen.csv'
        mode = 'a' if os.path.exists(filename) else 'w'
        with open(filename, mode, newline='') as csvfile:
            writer = csv.writer(csvfile)
            if mode == 'w':
                header_row = ['Generation'] + [f'Generation {i}' for i in range(self.generation + 1)]
                writer.writerow(header_row)
            writer.writerow([params_str] + average_count_by_gen)

        # plot the percentage of people who received the news
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.plot(range(self.generation + 1), average_count_by_gen)
        plt.xlabel('Generations')
        plt.ylabel('Percent of people has the rumor')
        plt.title(f'Percent of people with a rumor per the generation (average over {numruns} runs)')
        plt.subplots_adjust(top=0.8)
        plt.suptitle(params_str, fontsize=10, y=0.98)
        plt.show()
        sys.exit()


class GUI:
    def __init__(self):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the window and all of its widgets, including labels, entry boxes, and buttons.
    The default values for each parameter are set in this function as well.

    :param self: Refer to the object itself
    :param numofruns: Determine how many times the simulation will run
    :return: The window object
    """
        self.window = tk.Tk()
        self.window.title("Rumor Spreading Simulation")
        self.window.geometry("750x550")
        self.rumor_spreader = tk.StringVar()
        self.rumor_spreader.set("random")
        label_font = ("Arial", 18)  # Set the font for the labels
        entry_font = ("Arial", 16)  # Set the font for the entry boxes

        # Create labels and entry boxes for each parameter
        tk.Label(self.window, text="Population Density (P):",font=label_font,pady=10,anchor='w').grid(row=0, column=0)
        self.p_entry = tk.Entry(self.window,font=entry_font)
        self.p_entry.insert(0, str(default_p))  # Set default value
        self.p_entry.grid(row=0, column=1)

        tk.Label(self.window, text="Skepticism Level S4 (%):" ,font=label_font,pady=10,anchor='w').grid(row=1, column=0)
        self.s4_entry = tk.Entry(self.window,font=entry_font)
        self.s4_entry.insert(0, str(default_s4))  # Set default value
        self.s4_entry.grid(row=1, column=1)

        tk.Label(self.window, text="Skepticism Level S3 (%):",font=label_font,pady=10,anchor='w').grid(row=2, column=0)
        self.s3_entry = tk.Entry(self.window,font=entry_font)
        self.s3_entry.insert(0, str(default_s3))  # Set default value
        self.s3_entry.grid(row=2, column=1)

        tk.Label(self.window, text="Skepticism Level S2 (%):",font=label_font,pady=10,anchor='w').grid(row=3, column=0)
        self.s2_entry = tk.Entry(self.window,font=entry_font)
        self.s2_entry.insert(0, str(default_s2))  # Set default value
        self.s2_entry.grid(row=3, column=1)

        tk.Label(self.window, text="Skepticism Level S1 (%):",font=label_font,pady=10,anchor='w').grid(row=4, column=0)
        self.s1_entry = tk.Entry(self.window,font=entry_font)
        self.s1_entry.insert(0, str(default_s1))  # Set default value
        self.s1_entry.grid(row=4, column=1)

        tk.Label(self.window, text="Generations before re-transmission (L):",font=label_font,pady=10,anchor='w').grid(row=5, column=0)
        self.l_entry = tk.Entry(self.window,font=entry_font)
        self.l_entry.insert(0, str(default_l))  # Set default value
        self.l_entry.grid(row=5, column=1)

        tk.Label(self.window, text="Number of generations to simulate:",font=label_font,pady=10,anchor='w').grid(row=6, column=0)
        self.num_generations_entry = tk.Entry(self.window,font=entry_font)
        self.num_generations_entry.insert(0, str(default_num_generations))  # Set default value
        self.num_generations_entry.grid(row=6, column=1)

        # Add a label and a spinbox for the number of runs
        tk.Label(self.window, text="Number of Runs:", font=("Arial", 18), pady=10, anchor='w').grid(row=7, column=0)
        self.num_runs = tk.Entry(self.window, font=entry_font)
        self.num_runs.insert(0,str(default_numofruns))  # Set default value
        self.num_runs.grid(row=7, column=1)

        # Create a button to start the simulation
        self.start_button = tk.Button(self.window, text="Start Simulation",font=("Arial", 16),pady=10,anchor='w', width=13, height=2, command=self.start_simulation)
        self.start_button.grid(row=8, column=0, columnspan=2, pady=10)
        self.start_button.bind("<Enter>", self.on_enter)
        self.start_button.bind("<Leave>", self.on_leave)


    def on_enter(self, event):
        """
    The on_enter function is called when the mouse pointer enters the start_button widget.
    The function changes the background color of start_button to green and its foreground color to white.

    :param self: Represent the instance of the class
    :param event: Get the event that triggered this function
    :return: The button's background color and text color to their original values
    """
        self.start_button.config(bg="#4caf50", fg="#ffffff")

    def on_leave(self, event):
        """
    The on_leave function is a callback function that changes the color of the start button when
    the mouse leaves it. It takes in an event parameter, which is used to change the background and
    foreground colors of the start button.

    :param self: Represent the instance of the class
    :param event: Get the event that caused the function to be called
    :return: The start button with a white background and black text
    """
        self.start_button.config(bg="#ffffff", fg="#000000")

    def validate_input(self, parameter, value):
            """
    The validate_input function takes in a parameter and value, and checks to see if the value is valid for that parameter.
    If it is not valid, then False will be returned. If it is valid, True will be returned.

    :param self: Access the instance variables of the class
    :param parameter: Check which parameter is being validated
    :param value: Store the value of the parameter that is passed in
    :return: True if the input is valid, and false otherwise
    """
            if parameter == "p":
                try:
                    value = float(value)
                    if value < 0:
                        return False
                except ValueError:
                    return False

            elif parameter == "l":
                try:
                    value = int(value)
                    if not (0 <= value):
                        return False
                except ValueError:
                    return False
            elif parameter == "g":
                try:
                    value = int(value)
                    if not (0 <= value):
                        return False
                except ValueError:
                    return False
            elif parameter == "s":
                sum=0
                for s in value:
                    try:
                        sint = int(s)
                    except ValueError:
                        return False
                    sum+=sint
                if not (sum==100):
                    return False
            elif parameter == "n":
                try:
                    value = int(value)
                    if not (0 < value):
                        return False
                except ValueError:
                        return False
            return True
    def start_simulation(self):
        """
    The start_simulation function is called when the user clicks on the &quot;Start Simulation&quot; button.
    It takes in all of the values from each entry box and validates them to make sure they are within
    the acceptable range. If any value is not, it will use a default value instead and display a warning messagebox.
    If all values are valid, it will create an instance of the Simulation class with those parameters and call its run_simulation function.

    :param self: Refer to the instance of the class
    :return: The simulation
    """
        p = self.p_entry.get()
        s4 = self.s4_entry.get()
        s3 = self.s3_entry.get()
        s2 = self.s2_entry.get()
        s1 = self.s1_entry.get()
        l = self.l_entry.get()
        num_generations = self.num_generations_entry.get()
        num_runs=self.num_runs.get()
        if not self.validate_input("p",p):
            p = default_p
            messagebox.showwarning("Invalid Input", "Invalid value for Population Density. Using default value.")
        if not self.validate_input("l", l):
            messagebox.showwarning("Invalid Input",
                                   "Invalid value for Generations before re-transmission. Using default value.")
        if not self.validate_input("g", num_generations):
            num_generations = default_num_generations
            messagebox.showwarning("Invalid Input",
                                   "Invalid value for Number of generations to simulate. Using default value.")
        if not self.validate_input("s", [s1,s2,s3,s4]):
            s1 = default_s1
            s2=default_s2
            s3=default_s3
            s4=default_s4
            messagebox.showwarning("Invalid Input",
                                   "Invalid value for S1/S2/S3/S4 to simulate. Using default value.")
        if not self.validate_input("n", num_runs):
            num_runs = default_numofruns
            messagebox.showwarning("Invalid Input",
                                   "Invalid value for Number of runs to simulate. Using default value.")

        p = float(p)
        s4 = float(s4)/100
        s3 = float(s3)/100
        s2 = float(s2)/100
        s1 = float(s1)/100
        l = int(l)
        num_generations =int(num_generations)
        num_runs=int(num_runs)




        self.simulation = Simulation(p,[s4, s3, s2, s1],num_generations,l)  # Create instance of Simulation class

        # Call the simulation function with the specified parameters
        self.simulation.run_simulation(num_runs)

    def run(self):
        """
    The run function is the main loop of the program. It starts by creating a window object, which is an instance of
    the Tkinter class. The window object has many methods and attributes that can be used to customize it, such as its
    title or size. After this, we create a canvas widget on top of our window using the Canvas method from Tkinter. This
    canvas widget will be used to draw all shapes in our game onto it (such as circles for balls). We then create an
    instance of PongGame called pong_game and pass in self (which refers to this class)

    :param self: Represent the instance of the class
    :return: Nothing
    """
        self.window.mainloop()




class Person:
    def __init__(self,skepticism):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the object with all of its initial values.

    :param self: Represent the instance of the class
    :param skepticism: Determine the initial skepticism level of a node
    :return: The object itself
    """
        self.skepticism = skepticism
        self.received_rumor = False
        self.rumor_transmitted = False
        self.skepticism_level_decreased = False
        self.l=0
        self.approve_to_transmit=True



    def receive_rumor(self,gen):
        """
    The receive_rumor function is called when a node receives a rumor from another node.
    It sets the received_rumor attribute to True and records the generation of that rumor in
    the generation_received attribute.

    :param self: Refer to the object itself
    :param gen: Keep track of the generation number
    :return: The boolean value true
    """

        self.received_rumor = True
        self.generation_received=gen

    def transmit_rumor(self,L):
        """
    The transmit_rumor function is called when a node has been selected to transmit the rumor.
    The function sets the boolean value of rumor_transmitted to True, and sets approve_to_transmit
    to False. The function also takes in an integer L as an argument, which represents how many
    nodes will be infected by this transmission.

    :param self: Access the attributes and methods of the class in python
    :param L: Determine the number of times a rumor is transmitted
    :return: Nothing
    """
        self.rumor_transmitted = True
        self.approve_to_transmit = False
        self.l=L

    def decease_L(self):
        """
    The decease_L function decreases the value of L by 1.
    If L is 0, then it sets approve_to_transmit to True.

    :param self: Bind the method to an object
    :return: The value of the variable l
    """
        if(self.l>0):
            self.l=self.l-1
        if self.l==0:
            self.approve_to_transmit = True

    def decrease_skepticism_level(self):
        """
    The decrease_skepticism_level function decreases the skepticism level of a user by one.
        If the user is already at s0, then their skepticism level will not change.

    :param self: Refer to the object that is calling the function
    :return: Nothing
    """
        if self.skepticism == "s4":
            self.skepticism = "s3"
            self.skepticism_level_decreased = True
        elif self.skepticism == "s3":
            self.skepticism = "s2"
            self.skepticism_level_decreased = True
        elif self.skepticism == "s2":
            self.skepticism = "s1"
            self.skepticism_level_decreased = True

    def up_skepticism_level(self):
        """
    The up_skepticism_level function increases the skepticism level of a user by one.
        If the user's skepticism level has been decreased, then it will be increased to its original value.

    :param self: Access the attributes and methods of the class
    :return: The skepticism level of the user
    """
        if self.skepticism_level_decreased == True:
            if self.skepticism == "s3":
                self.skepticism = "s4"
            elif self.skepticism == "s2":
                self.skepticism = "s3"
            elif self.skepticism == "s1":
                self.skepticism = "s2"
        self.skepticism_level_decreased=False

    def reset(self):
        """
    The reset function is called at the beginning of each simulation.
    It resets all the variables that are used to keep track of what has happened in a single simulation.


    :param self: Represent the instance of the class
    :return: A list of the values of the variables that are reset
    """
        self.received_rumor = False
        self.rumor_transmitted = False
        self.skepticism_level_decreased = False
        self.l = 0
        self.approve_to_transmit = True

def main():
    """
The main function is the entry point of the program. It creates a GUI object and runs it.

:return: The gui object
"""
    gui = GUI()
    gui.run()




if __name__ == '__main__':
    main()




