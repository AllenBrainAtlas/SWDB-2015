from network import Network
import random

from scipy.sparse import csr_matrix
from allensdk.config.model.formats.hdf5_util import Hdf5Util

import numpy as np
import pandas as pd

import csv

# probabilities of establishing a connection from source -> target
connection_probabilities = { 
    ('excitatory', 'excitatory'): .3,
    ('excitatory', 'inhibitory'): .4,
    ('inhibitory', 'inhibitory'): .5,
    ('inhibitory', 'excitatory'): .5
}


def construct_matrix(connections):
    ''' turn a list of connection dictionaries into a numpy csr matrix '''
    cols = [ c['source'] for c in connections ]
    rows = [ c['target'] for c in connections ]
    data = [ c['nsyns'] for c in connections ]

    return csr_matrix((data, (rows, cols)))


def distance_probability(p1, p2):
    ''' convert euclidean distance to probability of connection '''
    dist = np.linalg.norm(p1 - p2, 2)
    return ( ( 1.0 - dist ) * 0.5 ) ** 1.2


def random_connectivity(src_i, tgt_i, source, target):
    ''' given a source target pair, create a connection (or not) '''
    pdist = distance_probability(positions[src_i],
                                 positions[tgt_i])

    p = connection_probabilities[source['type'],target['type']]

    if random.random() < p * pdist:
        return { 'nsyns': random.randrange(2, 6) }

N_exc = 8
N_inh = 2
N = N_inh + N_exc

# cell positions
positions = np.random.random((N,3))

# initialize the network
net = Network()

# add some populations
net.add_population(N_exc, type='excitatory')
net.add_population(N_inh, type='inhibitory')

# add the connectivity rule
net.connect(random_connectivity) 

# build the matrix
cells, connections = net.build()

print len(connections)

# turn it into a sparse matrix
if len(connections) > 0:
    m = construct_matrix(connections)
    print m

    # the connectivity to hdf5
    Hdf5Util().write('connections.h5', m)

cells = pd.DataFrame.from_dict(cells)
cells['x'] = positions[:,0]
cells['y'] = positions[:,1]
cells['z'] = positions[:,2]

cells.to_csv('cells.csv', index=False)

