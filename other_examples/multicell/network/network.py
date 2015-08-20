import random

class Network( object ):
    '''
    The Network class registers node types and connection rules
    in a lazy fashion without actually instantiating them.  
    when you're ready to build the whole list, use the build() method.
    '''
    
    def __init__(self):
        self.populations = []        
        self.connection_rules = []

        self.num_nodes = 0
    

    def add_population(self, count, **props):
        ''' 
        Add 'count' nodes to the network with properties specified 
        as a keyword args dictionary 
        '''

        self.populations.append(Population(count, props))
        self.num_nodes += count        
        

    def update_populations(self, props, update_props):
        '''
        Update the properties for nodes that match a set of properties    
        e.g. to assign layer 1 nodes to area v1:
            nw.update_populations({ 'layer': 1 }, { 'area': 'v1' })
        '''

        for pop in self.populations:
            if pop.matches_properties(props):
                pop.update(update_props)
                

    def update_populations_custom(self, filt, **update_props):          
        for pop in self.populations:
            if pop.matches_filter(filt):
                pop.update(update_props)
                
    def get_nodes(self, **props):
        ''' 
        Get a list of node gids that match certain property values             
        This returns a generator.
        '''

        nid = 0
        for pop in self.populations:            
            if pop.matches_properties(props):
                for i in xrange(nid, nid + pop.count):
                    yield i
            nid += pop.count
            

    def get_nodes_custom(self, filt):
        nid = 0
        for pop in self.populations:            
            if pop.matches_filter(filt):
                for i in xrange(nid, nid + pop.count):
                    yield i
            nid += pop.count            
            
    
    def connect(self, rule, **rule_kwargs):
        ''' Add a connection rule to the list. This does not actually run the rule. '''

        self.connection_rules.append({ 'function': rule, 'kwargs': rule_kwargs })
        

    def connect_pchain(self, pchain_rules, property_fn, **rule_kwargs):
        args = { 'pchain_rules': pchain_rules, 'property_fn': property_fn }
        args.update(rule_kwargs)
                
        self.connection_rules.append({ 'function': probability_chain_connector,
                                       'kwargs': args }) 
        
    def build(self):
        '''
        Convert the node type list and connection rule list
        into full lists of nodes and connections.
        '''

        nodes = []
        connections = []
        
        offset = 0        
        for pop in self.populations:
            for i in xrange(offset, offset+pop.count):
                node = { 'index': i }
                node.update(pop.properties)
                nodes.append(node)
                
            offset += pop.count
        
        for rule in self.connection_rules:
            rule_func = rule['function']
            rule_kwargs = rule['kwargs']
            
            src_offset = 0
            for source_pop in self.populations:
                for src_i in xrange(src_offset, src_offset + source_pop.count):
                    tgt_offset = 0
                    
                    for target_pop in self.populations:                    
                        for tgt_i in xrange(tgt_offset, tgt_offset + target_pop.count):
                            
                            connection = rule_func(src_i, tgt_i, 
                                                   source_pop.properties,
                                                   target_pop.properties,
                                                   **rule_kwargs)
                            
                            if connection:
                                connection_dict = { 'source': src_i,
                                                    'target': tgt_i }
                                
                                connection_dict.update(connection)
                                
                                connections.append(connection_dict)
                        
                        tgt_offset += target_pop.count
                
                src_offset += source_pop.count
        
        return nodes, connections        
       
    
class Population( object ):
    def __init__(self, count, properties):
        self.count = count
        self.properties = properties
    
    def __getitem__(self, index):
        return self.properties[index]
    
    def update(self, properties):
        self.properties.update(properties)
    
    def matches_properties(self, properties):        
        for k,v in properties.iteritems():
            if self.properties.get(k,None) != v:
                return False
        return True
    
    def matches_filter(self, filt):
        return filt(self.properties, self.count)
                        

def probability_chain_connector(src_i, tgt_i, 
                                source, target, 
                                pchain_rules, property_fn, **kwargs):
    p = 1.0
    for rule in pchain_rules:
        p *= rule(src_i, tgt_i, source, target, **kwargs)
        if p < 0:
            return None
        
    if random.random() < p:
        return property_fn(src_i, tgt_i, source, target, **kwargs)
    

class Index( object ):
    ''' Take a list of items and index them by property value for easy querying. '''

    def __init__(self):
        self.items = []
        self.index = {}
        
            
    def index_items(self, key):                
        index = {} 
        Index.grow_index(index, key, self.items)
        self.index[key] = index      
        
                
    def add_items(self, items):
        offset = len(self.items)
        self.items += items
                
        for key, key_index in self.index.iteritems():            
            Index.grow_index(key_index, key, items, offset)
            
    
    def get_ids(self, key, value):
        if key not in self.index:
            self.index_items(key)
        
        return self.index[key].get(value, [])
    
    
    def get_items(self, key, value):
        return [ self.items[i] for i in self.get_ids(key, value) ] 
    
    
    def get_values(self, key):
        if key not in self.index:
            self.index_items(key)
            
        return self.index[key].keys()
    
    
    @staticmethod
    def grow_index(index, key, items, offset=0):
        for i, item in enumerate(items):
            value = item.get(key, None)
            if value in index:
                index[value].append( i + offset )
            else:
                index[value] = [ i + offset ]                                 
