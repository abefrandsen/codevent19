import numpy as np

def get_fuel(mass):
    """
    Divide mass by 3, round down, subtract 2.
    
    i.e. get_fuel(14)=2
    """
    return np.maximum(np.floor(mass/3)-2,0)

# part 1
masses = np.loadtxt("p1_input.txt")
fuels = get_fuel(masses)
print("Part 1 answer: {}".format(int(fuels.sum())))


# part 2
masses = np.loadtxt("p1_input.txt")
fuels = get_fuel(masses)
tot_fuels = np.zeros(fuels.shape)
while fuels.sum()>0:
    tot_fuels += fuels
    fuels = get_fuel(fuels)
print("Part 2 answer: {}".format(int(tot_fuels.sum())))