import pylab as plt
import numpy as np

def Vm_traces(rec_vecs,db):

    '''
    plot voltage traces for all cells
    '''
    i_c=0; 
    
    fig1 = plt.figure(1)
    ax1=plt.subplot(1,1,1)
    time  = np.array(rec_vecs["t"])*1E-3

    # plot results:
    for gid in db.index:
        i_c+=1
        
        vm_shifted = np.array(rec_vecs["v"][gid]) - 100*i_c
        if db.ix[gid]['type']=='nr5a1': 
            line_color = 'r'
        if db.ix[gid]['type']=='pvalb': 
            line_color = 'b'
        
        
        plt.plot(time, vm_shifted, line_color); plt.hold(True)
        
        
    plt.xlabel('time (s)'); 
    
    plt.ylabel('Vm (mV)')
    
    
    Vspan = ax1.get_ylim()
    dVbar = 100 # scale = 100 mV
    t1=max(time)*0.90;  t2=t1; 
    y2=Vspan[0]*0.99; y1=y2+dVbar
    ax1.plot((t1, t2), (y1, y2), 'k-',lw=2)    
    ax1.text(t1*0.8, (y1+y2)/2, str(dVbar)+' mV', fontsize=12)
    
    ax1.set_yticklabels([])

    plt.xlim([0,time.max()])


def Vm_1trace(rec_vecs,db,gid):

    '''
    plot voltage traces for a single cell
    '''
    i_c=0; 
    
    fig2 = plt.figure(2)
    ax1=plt.subplot(1,1,1)
    time  = np.array(rec_vecs["t"])*1E-3

    vm = np.array(rec_vecs["v"][gid])

    if db.ix[gid]['type']=='nr5a1': 
        line_color = 'r'
    if db.ix[gid]['type']=='pvalb': 
        line_color = 'b'


    plt.plot(time, vm,line_color);
        
        
    plt.xlabel('time (s)'); 
    
    plt.ylabel('Vm (mV)')
    
    plt.xlim([0,time.max()])



    
    plt.show()

