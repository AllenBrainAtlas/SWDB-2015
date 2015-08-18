import sys
import csv
import pandas as pd
from allensdk.config.model.formats.hdf5_util import Hdf5Util
import scipy.sparse
from collections import Counter
import argparse

def write_vtk(file_name, cells, connections):
    index = 0
    cell_types = {}
    for cell in cells:
        if cell['type'] not in cell_types:
            cell_types[cell['type']] = index
            index += 1

    m = connections.tocoo()

    with open(file_name, 'wb') as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("really cool data\n")
        f.write("ASCII\n")
        f.write("DATASET POLYDATA\n")
        
        f.write("POINTS %d float\n" % len(cells))
        for cell in cells:
            f.write("%f %f %f\n" % ( cell['x'], cell['y'], cell['z'] ))

        print m.row
        print m.col
        print m.data

        f.write("LINES %d %d\n" % (len(m.row), len(m.row)*3))
        for i, j in zip(m.row, m.col):
            f.write("2 %d %d\n" % (i,j))

        f.write("\n")

        f.write("POINT_DATA %d\n" % len(cells))
        f.write("SCALARS angle float 1\n")
        f.write("LOOKUP_TABLE default\n")

        for cell in cells:
            f.write("%f\n" % cell['angle'])

        f.write("SCALARS cell_type int 1\n")
        f.write("LOOKUP_TABLE default\n")
        for cell in cells:
            f.write("%d\n" % cell_types[cell['type']])


        f.write("\n")

        f.write("CELL_DATA %d\n" % len(m.data))
        f.write("SCALARS weight float 1\n")
        f.write("LOOKUP_TABLE default\n")

        for d in m.data:
            f.write("%f\n" % d)

        f.write("\n")
            
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cells_csv', help='CSV containing cell metadata')
    parser.add_argument('connections_h5', help='HDF5 file containing cell connectivity')
    parser.add_argument('vtk_file', help='.vtk output file')

    args = parser.parse_args()

    # read in the cell CSV
    cells = pd.DataFrame.from_csv(args.cells_csv).to_dict(orient='records')

    # read in the connections from the H5 file
    h5u = Hdf5Util()
    connections = h5u.read(args.connections_h5)

    # write out the results
    write_vtk(args.vtk_file, cells, connections)
    

    

if __name__ == "__main__": main()
