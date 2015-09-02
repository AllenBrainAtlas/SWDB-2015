import os
from allensdk.api.queries.cell_types_api import CellTypesApi
import allensdk.core.swc as swc
import matplotlib.pyplot as plt
import numpy as np
import math
import pprint 
import csv

#output_file = 'sholl_all.csv'
#output_file = 'sholl_apical_dendrite_only.csv'
output_file = 'sholl_basal_dendrite_only.csv'

ct = CellTypesApi()

cells = ct.list_cells(require_reconstruction=True)
print "Cells with reconstructions: ", len(cells)

download_file = False
allow_types = [3]

radii = np.array(range(0,1000,10))
radii_square = np.square( radii )

#
# Computation based on line-sphere intersection formula
# https://en.wikipedia.org/wiki/Line%E2%80%93sphere_intersection
#

with open( output_file, 'wb' ) as csvfile :
    cwriter = csv.writer( csvfile, delimiter=',', quotechar='"' )
    header = ['cell_specimen_id', 'mouse_line', 'structure_acronym', 'graph_order', 'normalized_depth', 'ccf_soma_x', 'ccf_soma_y', 'ccf_soma_z']
    for r in radii :
        header.append( str(r) )
    cwriter.writerow( header )

    for idx, cell in enumerate(cells) :

        #if cell['id'] != 397351623:
        #    continue

        print '%d: %d' % (idx,cell['id'])
        fname = os.path.join( 'swc', '%d_morphology.swc' % cell['id'] )
        
        if download_file :
            ct.save_reconstruction( cell['id'], fname )
            
        morphology = swc.read_swc(fname)
        compartment_list = morphology.compartment_list
        
        root = compartment_list[0]
        if root['type'] != 1 :
            print 'first node is not soma'
            continue
            
        sholl = np.zeros( radii.shape )
        
        for n in morphology.compartment_list :
        
            node_soma_diff = np.array([root['x'],root['y'],root['z']]) - np.array([n['x'],n['y'], n['z']])
            node_soma_diff_norm = np.linalg.norm( node_soma_diff )
            node_soma_diff_norm_square = node_soma_diff_norm ** 2
            #print node_soma_diff
             
            child_nodes = [c for c in morphology.compartment_list if c['id'] in n['children']] 
            for cn in child_nodes:
            
                if not allow_types or cn['type'] not in allow_types :
                    continue
                    
                child_node_diff = np.array([cn['x'],cn['y'],cn['z']]) - np.array([n['x'],n['y'], n['z']])
                child_node_diff_norm = np.linalg.norm( child_node_diff )
                direction = child_node_diff / child_node_diff_norm
                #print direction
                
                dot = np.dot( direction, node_soma_diff )
                dot_square = np.square( dot )
                a = -1.0 * dot
                #print dot
                
                def number_of_crossing( r2 ) :
                    b = dot_square - node_soma_diff_norm_square + r2
                    
                    if b < 0 :
                        return 0
                    
                    b = math.sqrt( b )
                    
                    sol1 = False
                    if (a+b) >= 0 and (a+b) <= child_node_diff_norm :
                        sol1 = True
                        
                    sol2 = False
                    if (a-b) >= 0 and (a-b) <= child_node_diff_norm :
                        sol2 = True
                        
                    if sol1 and sol2 :
                        return 2
                    elif sol1 or sol2 :
                        return 1
                    else :
                        return 0
                        
                        
                nc = map( number_of_crossing, radii_square )
                    
                sholl = sholl + nc
            
        print sholl
        #pprint.pprint( cell )
        
        mouse_line = filter( lambda x: x['transgenic_line_type_name'] == 'driver', cell['donor']['transgenic_lines'] )[0]
        
        row = [cell['id'],mouse_line['name'],cell['structure']['acronym'],cell['structure']['graph_order'],
                cell['cell_soma_locations'][0]['normalized_depth'],
                cell['cell_soma_locations'][0]['x'],cell['cell_soma_locations'][0]['y'],cell['cell_soma_locations'][0]['z']]
        for s in sholl :
            row.append( str(s) )
        cwriter.writerow( row )
        

    



    
        
    

    
    
