from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
import pandas as pd
import numpy as np

def generate_matrix( mcc, experiments_df, structures_df, hemisphere_ids = [2,1],
                                   is_injection=False, parameter='projection_volume') :
    
    # generate data matrix
    rm = get_raw_matrix( mcc, experiments_df.id.values, structures_df.id.values, hemisphere_ids,
                        is_injection, parameter )
    
    # make column frame
    hlabel = {1:'L', 2:'R', 3:''}
    tt = zip(rm['columns'][:,1], rm['columns'][:,0])
    clabels = [ structures_df.loc[s]['acronym'] + '-' + hlabel[h] for s,h in tt]
    
    col_df = pd.DataFrame({'structure_id':rm['columns'][:,1], 
                           'hemisphere_id':rm['columns'][:,0],
                           'label': clabels} )
    
    output = {'matrix': rm['matrix'], 'columns':col_df }

    return output

    
def get_raw_matrix( mcc, experiment_ids, structure_ids, hemisphere_ids, is_injection, parameter):

    # multiple structure passing to get_structure_unionizes is not working
    # do my own filtering afterward
    su = mcc.get_structure_unionizes( experiment_ids, is_injection=is_injection )
    
    # structure filtering
    su = su[su['structure_id'].isin(structure_ids)]
        
    # hemisphere filtering
    su = su[su['hemisphere_id'].isin(hemisphere_ids)]
        
    # create np.array
    nrows = len(experiment_ids)
    ncolumns = len(structure_ids) * len(hemisphere_ids)
    
    pm = np.empty((nrows,ncolumns,))
    pm[:] = np.NAN
    
    # make lookup tables
    row_lookup={}
    for idx,e in enumerate(experiment_ids) :
        row_lookup[e] = idx
        
    column_lookup={}
    columns=np.empty((ncolumns,2),dtype=np.uint32)
    columns[:] = np.NAN
    cidx = 0
    for hidx,h in enumerate(hemisphere_ids) :
        for sidx,s in enumerate(structure_ids) :
            column_lookup[(h,s)] = cidx
            columns[cidx,0] = h
            columns[cidx,1] = s
            cidx += 1
            
    # loop through structure unionizes dataframe
    for row_index, row in su.iterrows():
        rindx = row_lookup[row['experiment_id']]
        k = (row['hemisphere_id'],row['structure_id'])
        cindx = column_lookup[k]
        pm[rindx,cindx] = row[parameter]
    
    return {'matrix':pm, 'rows':experiment_ids, 'columns':columns}
