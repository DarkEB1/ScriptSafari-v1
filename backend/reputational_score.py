"""
NOTE: Full Network rankings (nearest neighbour score) is recalculated recursively (calculate for every connection starting from node with one connection, and don't revisit nodes) every epoch (addition of tot/10 nodes) or on command
Nodes without neighbours are given a default score of (50) for the nearest neighbour score
For author: Store top citation, calculate as percentage of top citation
General ranking: aggregate all sub scores, find as percentage of maximum possible score
"""