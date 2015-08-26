import vtk

def preorder_traversal(root, compartments):
    nodestack = []
    nodelist = []

    node = root

    while True:
        nodelist.append(node)

        for childId in node['children']:
            child = compartments.get(childId, None)
            if child:
                nodestack.append(child)
            
        if len(nodestack) == 0:
            break
        else:
            node = nodestack.pop()
        
    return nodelist

def generate_polydata(compartments, root_compartment, minRadius=.25):
    import vtk
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    radii = vtk.vtkDoubleArray()
    radii.SetNumberOfComponents(1)
    radii.SetName("radius")

    types = vtk.vtkUnsignedCharArray()
    types.SetNumberOfComponents(1)
    types.SetName("type")

    compartment_ids = vtk.vtkUnsignedIntArray()
    compartment_ids.SetNumberOfComponents(1)
    compartment_ids.SetName("compartment_id")

    nodelist = preorder_traversal(root_compartment, compartments)

    pidmap = {}
    line = []

    root_pid = -1
    root_radius = 0

    for node in nodelist:

        if len(line) == 0 and node['parent'] != "-1":
            line.append(pidmap[node['parent']])

        pid = points.InsertNextPoint(node['x'], node['y'], node['z'])

        # keep track of the pid of the root node, as well as the radius of
        # one of its children.  We'll use that radius as a surrogate radius,
        # since dendrites don't actually have a cone shape
        if node['parent'] == "-1":
            root_pid = pid
            try:
                child = compartments[node['children'][0]]
                root_radius = child['radius']
            except BaseException as e:
                print(e)
                pass

        radii.InsertNextTuple1(max(node['radius'], minRadius))
        types.InsertNextTuple1(node['type'])
        compartment_ids.InsertNextTuple1(int(node['id']))

        pidmap[node['id']] = pid

        line.append(pid)
        if len(node['children']) == 0:
            lines.InsertNextCell(len(line))
            for i in line:
                lines.InsertCellPoint(i)
            line = []

    for p in xrange(1,points.GetNumberOfPoints()):
        p1 = points.GetPoint(p-1)
        p2 = points.GetPoint(p)

    # assuming we found a root, update its radius
    if root_radius > 0 and root_pid >= 0:
        radii.SetTuple1(root_pid, root_radius)

    polyData = vtk.vtkPolyData()
    polyData.SetPoints(points)
    polyData.SetLines(lines)
    polyData.GetPointData().AddArray(radii)
    polyData.GetPointData().AddArray(types)
    polyData.GetPointData().AddArray(compartment_ids)
    polyData.GetPointData().SetActiveScalars("radius")

    return polyData

def save_polydata(pd, file_name):
    print file_name
    f = vtk.vtkPolyDataWriter()
    f.SetInput(pd)
    f.SetFileName(file_name)
    f.Update()

def merge_polydata(pds):
    f = vtk.vtkAppendPolyData()
    for pd in pds:
        f.AddInput(pd)
    f.Update()

    return f.GetOutput()
