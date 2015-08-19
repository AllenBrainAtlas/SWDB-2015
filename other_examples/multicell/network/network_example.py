from network import Network
import random

from scipy.sparse import csr_matrix
from allensdk.config.model.formats.hdf5_util import Hdf5Util

import numpy as np
import csv

# probabilities of establishing a connection from source -> target
connection_probabilities = { 
    ('excitatory', 'excitatory'): .75,
    ('excitatory', 'inhibitory'): .25,
    ('inhibitory', 'inhibitory'): .1,
    ('inhibitory', 'excitatory'): .5
}

# function for turning a list of connection dictionaries into a 
# sparse matric
def construct_matrix(connections):
    rows = [ c['source'] for c in connections ]
    cols = [ c['target'] for c in connections ]
    data = [ c['weight'] for c in connections ]

    return csr_matrix((data, (rows, cols)))

# given a source target pair, create a connection (or not)
def random_connectivity(src_i, tgt_i, source, target):
    p = connection_probabilities[source['ctype'],target['ctype']]
    if random.random() < p:
        return { 'weight': random.random() }

# initialize the network
net = Network()

# add some populations
net.add_population(10, ctype='inhibitory')
net.add_population(30, ctype='excitatory')

# add the connectivity rule
net.connect(random_connectivity) 

# build the matrix
cells, connections = net.build()

# turn it into a sparse matrix
m = construct_matrix(connections)

# the connectivity to hdf5
Hdf5Util().write('connections.h5', m)

# write the cell info to csv
with open('cells.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=['index','ctype'])
    w.writeheader()
    for c in cells:
        w.writerow(c)

