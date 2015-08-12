# Multicell Example

The code simulates a 10 cell connected network where each cell is stimulated with the current clamp.

Each cells is associated with a unique gid which is used to identify each cell.

The input to the model is provided in the `input/` directory:

* `db10cells.csv` - cell data base (type, coordinates, etc.)
* `loc_con.hdf5`  - cell-to-cell connectivity
* `stimulus.json` - current clamp parameters
 
The additional configuration of the model is in `config.json`.

The code uses AllenSDK modules which needs to be installed to run the code.


## To run (on Linux):

    nrnivmodl modfiles # (do once to create an x86 folder or after changing the mod files)
    
    python main.py # (or nrniv -python main.py)


