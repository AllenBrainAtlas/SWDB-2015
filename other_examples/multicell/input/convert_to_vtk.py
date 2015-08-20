import sys
import csv
import pandas as pd
from allensdk.config.model.formats.hdf5_util import Hdf5Util
import scipy.sparse
from collections import Counter
import argparse

SKIP_FIELDS = ['x', 'y', 'z', 'index', 'gid']

def get_vtk_dtype(obj):
    try:
        int(obj)
        return 'int'
    except ValueError:
        try:
            float(obj)
            return 'float'
        except ValueError:
            return 'string'

def convert_string_types_to_int(cells, field):
    index = 0
    values = {}
    for cell in cells:
        if cell[field] not in values:
            values[cell[field]] = index
            index += 1

    for cell in cells:
        cell[field] = values[cell[field]]

def write_vtk(file_name, cells, connections):
    scalar_fields = [ ( k, get_vtk_dtype(v) ) for k,v in cells[0].iteritems() if k not in SKIP_FIELDS ]

    for i, (field, dtype) in enumerate(scalar_fields):
        if dtype == 'string':
            convert_string_types_to_int(cells, field)
            scalar_fields[i] = (field, 'int')

    m = connections.tocoo()

    with open(file_name, 'wb') as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("really cool data\n")
        f.write("ASCII\n")
        f.write("DATASET POLYDATA\n")
        
        f.write("POINTS %d float\n" % len(cells))
        for cell in cells:
            f.write("%s %s %s\n" % ( cell['x'], cell['y'], cell['z'] ))

        f.write("LINES %d %d\n" % (len(m.row), len(m.row)*3))
        for i, j in zip(m.row, m.col):
            f.write("2 %d %d\n" % (i,j))

        f.write("\n")

        if len(scalar_fields):
            f.write("POINT_DATA %d\n" % len(cells))

            for field, dtype in scalar_fields:
                f.write("SCALARS %s %s 1\n" % (field, dtype))
                f.write("LOOKUP_TABLE default\n")

                for cell in cells:
                    f.write("%s\n" % cell[field])

                f.write("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cells_csv', help='CSV containing cell metadata')
    parser.add_argument('connections_h5', help='HDF5 file containing cell connectivity')
    parser.add_argument('vtk_file', help='.vtk output file')

    args = parser.parse_args()

    # read in the cell CSV
    with open(args.cells_csv, 'r') as f:
        r = csv.DictReader(f)
        cells = list(r)

    # read in the connections from the H5 file
    h5u = Hdf5Util()
    connections = h5u.read(args.connections_h5)

    # write out the results
    write_vtk(args.vtk_file, cells, connections)
    

    

if __name__ == "__main__": main()
