def distance_between_points_2d(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return (dx**2 + dy**2)**.5

# we'll use this later
def neuron():
    print "inside neuron function!"

def main():
    p1 = (1,2)
    p2 = (3,4)

    print distance_between_points_2d(p1,p2)

    p3 = (4,5)
    p4 = (2,3)

    print distance_between_points_2d(p3,p4)


# __name__ is a built-in global variable.  if it == __main__, 
# that means your file is being run from the command line.
# Otherwise, your file is being imported.
if __name__ == "__main__": main()

