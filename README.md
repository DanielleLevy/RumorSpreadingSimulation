# RumorSpreadingSimulation

##Getting Started- Instructions
Based Windows
write the following in the terminal and press enter:
git clone https://github.com/DanielleLevy/RumorSpreadingSimulation.git
###2 Ways to run:
####first way:

write the following in the terminal , after each one press enter: 
1.cd dist
2. ./RumorSpreadingSimulation.exe


####second way:

Go to the folder where the Repo file is located, enter the DIST folder, and double-click on the EXE file.

## Description:
The automaton is designed on a grid of 100 x 100 cells. The cells are uniformly distributed with a density parameter P, which represents the population density and can be varied throughout the research to study its effect on the system's behavior.

Each person in the population has a level of skepticism, which is defined as one of four levels:

S4: does not believe any rumor
S3: believes a rumor with a basic probability of 1/3
S2: believes a rumor with a basic probability of 2/3
S1: believes any rumor
Each person is randomly assigned a level of skepticism, and the task is to decide what percentage of the population falls into each skepticism level.

A random person is selected from the population to start spreading a rumor according to the following rules:

When a person spreads a rumor, they pass it on to all their neighbors.
When a person receives a rumor, they decide whether to pass it on to their neighbors based on their level of skepticism. For example, if a person has a skepticism level of S2 and receives a rumor, they have a 1/3 chance of passing it on to their neighbors. The transmission occurs immediately after receiving the rumor.
If a person receives the same rumor from at least two different neighbors in the same generation, their skepticism level temporarily decreases. For example, if a person has a basic skepticism level of S3 and receives the same rumor from two neighbors in the same generation, their skepticism level will temporarily become S2.
A person who has already passed on a rumor will not pass it on again for L generations, where L is another parameter that can be varied in the research.
After L generations, a person can pass on the rumor again if they receive it again.

