import os
import numpy as np
import nrrd

def get_transform_matrix(p) :
    m = np.zeros((4,4),dtype=np.float)
    m[3,3] = 1.0
    m[0:3,0:3] = np.reshape(p[0:9],(3,3))
    m[0:3,3:4] = np.reshape(p[9:12],(3,1))
    return m


def create_morphology_volumes( compartment_list, parameters, output_directory, laplacian, mask, resolution=10.0 ) :

    compartment_dict = {}
    for n in compartment_list :
        compartment_dict[n['id']] = n
        
    transform = get_transform_matrix(parameters)
    types = zip([2,3,4],['axon','basal_dendrite','apical_dendrite'])
    
    # find soma depth
    soma_depth = None
    for n in compartment_list :
        if n['type'] == 1 :
            n_pos = n_pos = np.array([n['x'],n['y'],n['z'],1])
            n_pos = np.dot(transform,n_pos)
            n_pos = n_pos[0:3]
            r = np.round( n_pos/resolution )
            if mask[tuple(r)] :
                soma_depth = laplacian[tuple(r)]
                
    #print "soma depth: " + str(soma_depth)
    
    for t in types :
    
        # initialize
        pt_dict = {}
        
        for n in compartment_list :
            if n['type'] == t[0] :
                n_pos = np.array([n['x'],n['y'],n['z'],1])
                n_pos = np.dot(transform,n_pos)
                p = compartment_dict[n['parent']]
                p_pos = np.array([p['x'],p['y'],p['z'],1])
                p_pos = np.dot(transform,p_pos)
                
                n_pos = n_pos[0:3]
                p_pos = p_pos[0:3]
                
                diff = n_pos - p_pos
                dist = np.linalg.norm(diff)
                diff = diff/dist
                c = 0
                while c < (dist + 0.5*resolution) :
                    a = n_pos + c * diff
                    r = np.round( a/resolution )
                    if mask[tuple(r)] :
                        pt_dict[tuple(r)] = laplacian[tuple(r)]
                    c = c + 0.5*resolution
         
        output = [ v for k,v in pt_dict.iteritems() ]
        h, e = np.histogram( output, 100, [0,1] )
        fname = os.path.join( output_directory, '%s.npy' % t[1] )
        np.save( fname, h )
        
        h, e = np.histogram( output - soma_depth, 200, [-1,1] )
        fname = os.path.join( output_directory, '%s_shifted.npy' % t[1] )
        np.save( fname, h )
        
