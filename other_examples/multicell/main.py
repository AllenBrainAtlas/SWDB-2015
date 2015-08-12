import pylab as plt
import visual as vis

from allensdk.model.biophys_sim.config import Config
from utils import Utils


config = Config().load('config.json')   # read configuration for the model

utils = Utils(config)   # instantiate an object of a class Utils which configures NEURONand provides the interface to the necessary functions to set up the simuation
h = utils.h


db = utils.load_cell_db()

cells = utils.generate_cells(db)	# read cell information from csv file


print "load connectivity:"
con = utils.load_connectivity()
 
print 'connecting cells:'
[netcons,syns]= utils.connect_cell(cells,db,con)
print '# of netcons, syns: ',len(netcons), len(syns)


utils.set_run_params()  # set h.dt and h.tsop


print "setting stimulus:"
stims = utils.setIClamps(cells)

print "set recordings"
rec_vecs = utils.record_values(cells)


print "run the model for %.1f (ms) with step %.3f (ms):" %(h.tstop, h.dt)
h.finitialize()
h.run()


print "plotting results:"
vis.Vm_traces(rec_vecs,db)

plt.show()


