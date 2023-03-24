from shapely.geometry import LineString, Point
from math import  atan2, pi, sqrt

def computeLengthLinestring(line, method = "haversine"): 
    """
     Returns the length of the linestring [line], using the [method].
    
     Parameters
     ----------
     line : LineString
     method : string 
        determines how to compute the length between points (e.g, haversine or euclidean)

     Returns
     -------
     distance : float
         length of the [line]
    
    """
    # Extract all coordinates
    numCoords = len(line.coords) - 1
    
    distance = 0
    for i in range(0, numCoords):
        point1 = line.coords[i]
        point2 = line.coords[i + 1]
        if method == "haversine": distance += haversine(point1[0], point1[1], point2[0], point2[1])
        else: distance += sqrt((point1[0]-point2[0])**2 + (point1[1] - point2[1])**2)
    return distance
def computeBearing(start_point, end_point):
    """
    This function computes the bearing between two points: [start_point] and [end_point].
    
    Parameters
    ----------
    start_point : Point(x,y)
    end_point : Point(x,y)
    
    Returns
    -------
    brng_new : float
    
    """
    brng_new = (180/pi) * atan2(end_point.x-start_point.x, end_point.y - start_point.y)
    if brng_new >= 0: return brng_new
    else: return brng_new+360
def computeAngularDifference(alpha, beta):
    """
     Returns the angular difference between the angles [alpha] and [beta] (in degrees)
    
     Parameters
     ----------
     alpha : float
         Angle 1 in degrees
     beta : float
         Angle 2 in degrees

     Returns
     -------
     check : float
         angular difference in degrees
    
    """
    check = abs(float(alpha)-float(beta))
    if check > 180: check = abs(check- 360)
    return check

def _is_self_loop(G, edge, bool_ = False):
    u, v, k = edge[0],edge[1],edge[2]
    if (u==v) and edge[3]['length']==0:
        if bool_: return True
        else: # remove the edge
            G.remove_edge(u,v,k)
    if bool_: return False
    else: return G

def _is_easy_interstitual(G, node, bool_ = False):
    neighbors = set(list(G.predecessors(node)) + list(G.successors(node)))
    n = len(neighbors) 
    
    # Compare in and out degrees to see which nodes to consider
    if (G.in_degree(node) == 1 and G.out_degree(node) == 1 and n==2):
        # Find the incoming edge
        inedge = list(G.in_edges(node, keys = True, data = True))
        geom_in_old = inedge[0][3]['geometry']
        geom_in_old = geom_in_old.simplify(tolerance=0, preserve_topology=True).coords
        geom_in = []
        [geom_in.append(x) for x in geom_in_old]
        second_last_point, last_point = Point(geom_in[-2]), Point(geom_in[-1])
        brng_incoming = computeBearing(second_last_point, last_point)
        #print("Bearing incoming: ", brng_incoming)
        
        # Find the outgoing edge
        outedge = list(G.out_edges(node, keys = True, data = True))
        geom_out_old = outedge[0][3]['geometry']  
        geom_out_old = geom_out_old.simplify(tolerance=0, preserve_topology=True).coords
        geom_out = []
        [geom_out.append(x) for x in geom_out_old]
        first_point, second_point = Point(geom_out[0]), Point(geom_out[1])
        brng_outgoing = computeBearing(first_point, second_point)
        #print("Bearing outgoing: ", brng_outgoing)
        
        # Keep information about whether the edge is newly added
        in_new, out_new = inedge[0][3]['new'], outedge[0][3]['new']
        in_driven, out_driven = inedge[0][3]['driven'], outedge[0][3]['driven']
        
        # print(inedge[0][3])
        # print(inedge[0][3]['highway'])
        #in_highway, out_highway = inedge[0][3]['highway'], outedge[0][3]['highway']
        
        try: in_highway = inedge[0][3]['highway']
        except: in_highway = "-"
        try: out_highway = outedge[0][3]['highway']
        except: out_highway = "-"
        
        ##################### When lengths do not align #####################
        a = computeLengthLinestring(inedge[0][3]['geometry'], method = 'euclidean') #computeLengthLinestring(LineString(geom_in), method = 'euclidean')
        in_length = inedge[0][3]['length']
        if round(a,5)!=round(in_length,5):
            print(inedge)
            print(a)
            print(in_length)
            print("----")
            stop
        b = computeLengthLinestring(outedge[0][3]['geometry'], method = 'euclidean') #computeLengthLinestring(LineString(geom_out), method = 'euclidean')
        out_length = outedge[0][3]['length']
        if round(b,5)!=round(out_length,5): 
            print(outedge)
            print(b)
            print(out_length)
            print("----")
            stop
        #####################################################################    
       
        if (computeAngularDifference(brng_incoming,brng_outgoing)<90) and (in_new == out_new) and (in_highway == out_highway): # In this case, the node can be removed. 
            if bool_: return True
            else: # remove the node
                # Create the new edge
                keyNew = max([item[2] for item in G.edges(inedge[0][0], outedge[0][1], keys = True) if ((item[0] == inedge[0][0]) & (item[1] == outedge[0][1]))], default=-1) + 1
                newgeom = LineString(geom_in[:-1] + geom_out)
                G.add_edge(inedge[0][0], outedge[0][1], highway = in_highway, new = in_new, driven = in_driven|out_driven, geometry = newgeom, length=computeLengthLinestring(newgeom, method = 'euclidean'), key = keyNew)
                
                ##################### When lengths do not align #####################
                if round(in_length+out_length,0) != round(computeLengthLinestring(newgeom, method = 'euclidean'),0): 
                    print(inedge)
                    print(inedge[0][3]['geometry'])
                    print(in_length)
                    print(a)
                    print("--")
                    print(outedge)
                    print(outedge[0][3]['geometry'])
                    print(out_length)
                    print(b)
                    print(in_length+out_length)
                    print(computeLengthLinestring(newgeom, method = 'euclidean'))
                    stop
                #####################################################################
                
                # remove the node
                G.remove_node(node)
                return G
            
    if bool_: return False
    else: return G

def _is_difficult_interstitual(G, node, bool_ = False):
    
    predessors = list(G.predecessors(node))
    successors = list(G.successors(node))
    
    neighbors = set(list(G.predecessors(node)) + list(G.successors(node)) + [node])
    neighbors.remove(node)
    n = len(neighbors)
    
    c = 0
    if (G.in_degree(node) == 2 and G.out_degree(node) == 2 and n==2 and (set(predessors) == set(successors))):#len(predessors)==len(successors)):
        # Find the incoming/outgoing edges
        inedges = list(G.in_edges(node, keys = True, data = True))
        outedges = list(G.out_edges(node, keys = True, data = True))
        
        # Add the two edges: from start_point of the first and second incoming edge. 
        count = 0
        for inedge in inedges:   
            if outedges[0][1]==inedge[0]: outedge = outedges[1]
            else: outedge = outedges[0]
            
            # Find the incoming edge
            geom_in_old = inedge[3]['geometry']#.coords
            geom_in_old = geom_in_old.simplify(tolerance=0, preserve_topology=True).coords
            geom_in = []
            [geom_in.append(x) for x in geom_in_old]
            second_last_point, last_point = Point(geom_in[-2]), Point(geom_in[-1])
            brng_incoming = computeBearing(second_last_point, last_point)
            #print("Bearing incoming: ", brng_incoming)
            
            # Find the outgoing edge
            geom_out_old = outedge[3]['geometry']
            geom_out_old = geom_out_old.simplify(tolerance=0, preserve_topology=True).coords
            geom_out = []
            [geom_out.append(x) for x in geom_out_old]
            first_point, second_point = Point(geom_out[0]), Point(geom_out[1])
            brng_outgoing = computeBearing(first_point, second_point)
            #print("Bearing outgoing: ", brng_outgoing)
            
            # Keep information about whether the edge is newly added
            in_new, out_new = inedge[3]['new'], outedge[3]['new']
            in_driven, out_driven = inedge[3]['driven'], outedge[3]['driven']
            #in_highway, out_highway = inedge[3]['highway'], outedge[3]['highway']
            try: in_highway = inedge[3]['highway']
            except: in_highway = "-"
            try: out_highway = outedge[3]['highway']
            except: out_highway ="-"
            
            ##################### When lengths do not align #####################
            a = computeLengthLinestring(inedge[3]['geometry'], method = 'euclidean') #computeLengthLinestring(LineString(geom_in), method = 'euclidean')
            in_length = inedge[3]['length']
            if round(a,2)!=round(in_length,2):
                print(inedge)
                print(a)
                print(in_length)
                print("----")
                stop
            b = computeLengthLinestring(outedge[3]['geometry'], method = 'euclidean') #computeLengthLinestring(LineString(geom_out), method = 'euclidean')
            out_length = outedge[3]['length']
            if round(b,2)!=round(out_length,2):
                print(outedge)
                print(b)
                print(out_length)
                print("----")
                stop
            #####################################################################

            if (computeAngularDifference(brng_incoming,brng_outgoing) < 90 and (in_highway == out_highway) and (in_new == out_new)) or (count == 1):
                count+=1
                if bool_: return True
                else: # remove the node
                    # Create the new edge
                    keyNew = max([item[2] for item in G.edges(inedge[0], outedge[1], keys = True) if ((item[0] == inedge[0]) & (item[1] == outedge[1]))], default=-1) + 1
                    newgeom = LineString(geom_in[:-1] + geom_out)
                    G.add_edge(inedge[0], outedge[1], highway= in_highway, new = in_new, driven = in_driven|out_driven, geometry = newgeom, length=computeLengthLinestring(newgeom, method = 'euclidean'), key = keyNew)
                    
                    # Hier nog effe checken of dit goed gaat. 
                    ##################### When lengths do not align #####################
                    if round(in_length+out_length,5) != round(computeLengthLinestring(newgeom, method = 'euclidean'),5): 
                        print(in_length+out_length)
                        print(geom_in_old.xy)
                        print(geom_out_old.xy)
                        print("=")
                        print(newgeom.coords.xy)
                        print(computeLengthLinestring(newgeom, method = 'euclidean'))
                        print("===")
                    #####################################################################
                    
                    # If we do it for one way, we have to do it for the other way around, even if angular diff > 90...
                    c = 1
                    
            else: 
                if bool_: return False
                else: return G, c
        
        # remove the node
        G.remove_node(node)
    
    if bool_: return False
    else: return G, c

def _remove_nodes_undirected(G, node, bool_ = False):
    # Consider only possible points indicated by the is_end function from OSMnx
    #print(node +":", _is_endpoint(G, node, strict=True))
    #if not _is_endpoint(G, node, strict=True):
    neighbors = list(set(list(G.predecessors(node)) + list(G.successors(node))))
    n = len(neighbors)
    d = G.degree(node)
    
    # Compare in and out degrees to see which nodes to consider
    if ((G.in_degree(node) + G.out_degree(node) == 2) and n==2):#(G.in_degree(node) == 1 and G.out_degree(node) == 1 and n==2):
        inoutedges = list(G.in_edges(node, data = True, keys = True)) + list(G.out_edges(node, data = True, keys = True))
        
        # Since the graph is undirected, we need to carefully find out which edge is incoming and which outgoing, and adjust linestrings accordingly
        start_node, end_node = neighbors[0], neighbors[1]
        if start_node in inoutedges[0][0:2]:
            if start_node == inoutedges[0][0]: inedge = inoutedges[0]
            else: inedge = (inoutedges[0][1], node, inoutedges[0][2], {'highway': 'unclassified', 'oneway': False, 'length': inoutedges[0][3]['length'], 'geometry': LineString(list(inoutedges[0][3]['geometry'].coords)[::-1]), 'close_to_point_start': '-', 'close_to_point_end': '-', 'new': inoutedges[0][3]['new']})
        elif start_node in inoutedges[1][0:2]:
            if start_node == inoutedges[1][0]: inedge = inoutedges[1]
            else: inedge = (inoutedges[1][1], node, inoutedges[1][2], {'highway': 'unclassified', 'oneway': False, 'length': inoutedges[1][3]['length'], 'geometry': LineString(list(inoutedges[1][3]['geometry'].coords)[::-1]), 'close_to_point_start': '-', 'close_to_point_end': '-', 'new': inoutedges[1][3]['new']})
        if end_node in inoutedges[0][0:2]:
            if end_node == inoutedges[0][0]: outedge = (node, inoutedges[0][0], inoutedges[0][2], {'highway': 'unclassified', 'oneway': False, 'length': inoutedges[0][3]['length'], 'geometry': LineString(list(inoutedges[0][3]['geometry'].coords)[::-1]), 'close_to_point_start': '-', 'close_to_point_end': '-', 'new': inoutedges[0][3]['new']})
            else: outedge = inoutedges[0]   
        elif end_node in inoutedges[1][0:2]:
            if end_node == inoutedges[1][0]: outedge = (node, inoutedges[1][0], inoutedges[1][2], {'highway': 'unclassified', 'oneway': False, 'length': inoutedges[1][3]['length'], 'geometry': LineString(list(inoutedges[1][3]['geometry'].coords)[::-1]), 'close_to_point_start': '-', 'close_to_point_end': '-', 'new': inoutedges[1][3]['new']})
            else: outedge = inoutedges[1]
            
        # Find the incoming edge
        geom_in_old = inedge[3]['geometry']
        geom_in_old = geom_in_old.simplify(tolerance=0, preserve_topology=True).coords
        geom_in = []
        [geom_in.append(x) for x in geom_in_old]
        second_last_point, last_point = Point(geom_in[-2]), Point(geom_in[-1])
        brng_incoming = computeBearing(second_last_point, last_point)
        #print("Bearing incoming: ", brng_incoming)
    
        # Find the outgoing edge
        geom_out_old = outedge[3]['geometry']  
        geom_out_old = geom_out_old.simplify(tolerance=0, preserve_topology=True).coords
        geom_out = []
        [geom_out.append(x) for x in geom_out_old]
        first_point, second_point = Point(geom_out[0]), Point(geom_out[1])
        brng_outgoing = computeBearing(first_point, second_point)
        #print("Bearing outgoing: ", brng_outgoing)
    
        # Keep information about whether the edge is newly added
        in_new, out_new = inedge[3]['new'], outedge[3]['new']
    
        ##################### When lengths do not align #####################
        a = computeLengthLinestring(inedge[3]['geometry'], method = 'euclidean') #computeLengthLinestring(LineString(geom_in), method = 'euclidean')
        in_length = inedge[3]['length']
        if round(a,2)!=round(in_length,2):
            print(inedge)
            print(a)
            print(in_length)
            print("----")
            stop
        b = computeLengthLinestring(outedge[3]['geometry'], method = 'euclidean') #computeLengthLinestring(LineString(geom_out), method = 'euclidean')
        out_length = outedge[3]['length']
        if round(b,2)!=round(out_length,2): 
            print(outedge)
            print(b)
            print(out_length)
            print("----")
            stop
        #####################################################################    
   
        if (computeAngularDifference(brng_incoming,brng_outgoing)<90) and (in_new == out_new): # In this case, the node can be removed. 
            if bool_: return True
            else: # remove the node
                # Create the new edge
                newgeom = LineString(geom_in[:-1] + geom_out)
                if computeLengthLinestring(newgeom, method = 'euclidean') != in_length+out_length: newgeom = LineString(geom_out[:-1] + geom_in)
           
                G.add_edge(inedge[0], outedge[1], new = in_new, geometry = newgeom, length=computeLengthLinestring(newgeom, method = 'euclidean'))
                #print(inedge[0], "->", outedge[1])
                ##################### When lengths do not align #####################
                if (round(in_length+out_length,0) != round(computeLengthLinestring(newgeom, method = 'euclidean'),0)): 
                    print(inedge)
                    print(inedge[3]['geometry'])
                    print(in_length)
                    print(a)
                    print("--")
                    print(outedge)
                    print(outedge[3]['geometry'])
                    print(out_length)
                    print(b)
                    print(in_length+out_length)
                    print(computeLengthLinestring(newgeom, method = 'euclidean'))
                    stop
                #####################################################################
            
                # remove the node
                G.remove_node(node)
                return G
  
    if bool_: return False
    else: return G

def _is_endpoint(G, node, strict=True):
    """
    Is node a true endpoint of an edge.

    Return True if the node is a "real" endpoint of an edge in the network,
    otherwise False. OSM data includes lots of nodes that exist only as points
    to help streets bend around curves. An end point is a node that either:
    1) is its own neighbor, ie, it self-loops.
    2) or, has no incoming edges or no outgoing edges, ie, all its incident
    edges point inward or all its incident edges point outward.
    3) or, it does not have exactly two neighbors and degree of 2 or 4.
    4) or, if strict mode is false, if its edges have different OSM IDs.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    node : int
        the node to examine
    strict : bool
        if False, allow nodes to be end points even if they fail all other rules
        but have edges with different OSM IDs

    Returns
    -------
    bool
    """
    neighbors = set(list(G.predecessors(node)) + list(G.successors(node)))
    n = len(neighbors)
    d = G.degree(node)

    #print("Examining node: ", node)
    #print("Neighbours: ", neighbors)
    # rule 1
    if node in neighbors:
        #print("Rule 1")
        # if the node appears in its list of neighbors, it self-loops
        # this is always an endpoint.
        return True

    # rule 2
    elif G.out_degree(node) == 0 or G.in_degree(node) == 0:
        #print("Rule 2")
        # if node has no incoming edges or no outgoing edges, it is an endpoint
        return True

    # rule 3
    elif not (n == 2 and (d == 2 or d == 4)):
        #print("Rule 3")
        # else, if it does NOT have 2 neighbors AND either 2 or 4 directed
        # edges, it is an endpoint. either it has 1 or 3+ neighbors, in which
        # case it is a dead-end or an intersection of multiple streets or it has
        # 2 neighbors but 3 degree (indicating a change from oneway to twoway)
        # or more than 4 degree (indicating a parallel edge) and thus is an
        # endpoint
        return True

    # rule 4
    elif not strict:
        print("Rule 4")
        # non-strict mode: do its incident edges have different OSM IDs?
        osmids = []

        # add all the edge OSM IDs for incoming edges
        for u in G.predecessors(node):
            for key in G[u][node]:
                osmids.append(G.edges[u, node, key]["osmid"])

        # add all the edge OSM IDs for outgoing edges
        for v in G.successors(node):
            for key in G[node][v]:
                osmids.append(G.edges[node, v, key]["osmid"])

        # if there is more than 1 OSM ID in the list of edge OSM IDs then it is
        # an endpoint, if not, it isn't
        return len(set(osmids)) > 1

    # if none of the preceding rules returned true, then it is not an endpoint
    else:
        return False

