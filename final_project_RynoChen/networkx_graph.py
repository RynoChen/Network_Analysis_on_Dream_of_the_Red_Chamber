import networkx as nx
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

G_1=nx.Graph() # create the graph object

# obtain the information stored in "DataFrame" with the help of Pandas
nodes=pd.read_csv("nodes_relationships.tsv",sep='\t')   # sep='\t' as they're tsv files
edges=pd.read_csv("edges_relationships.tsv",sep='\t')

# create a correspondance between homes and color
# colors are coded in hex indeces; reference: https://www.color-hex.com
# the color list may need to be extended manualy  accordingly; for this project, both of them are created long enough
color_list_node = ["#f9f7af", "#ffbaed", "#05c76a", "#e0d6ff",  "#ffa500", "#afafaf", '#6897bb']
                    # yellow,   #pink,  #limegreen,   #violet,   #orange,   #grey,     #lightblue
color_list_edge = ["#ff0000", "#00008b", "#006400", "#ff8c00", "#f4a460", "#696969"]
                    #"red",    "blue",    "green",   "orange",  "sandy",    "grey"
home_list = list(set(nodes["Home"])) # use set to create a group of non-duplicated homes; turn it into list for future indexing
color_dict_1={} # the dict for node_color correpondance
for i in range(len(home_list)):
    color_dict_1[home_list[i]]=color_list_node[i]
relation_list=list(set(edges["Relation"]))
color_dict_2={} # the dict for edge_color correpondance
for i in range(len(relation_list)):
    color_dict_2[relation_list[i]]=color_list_edge[i]
# NOTE: the operation "set" randomized the sequence order; resulting in random color-correspondance;
#       will be solved if a legend is created, which is not the case for this script, which is an admitted flaw
#       the correpondance can be figured out by observing the graph & original tsv forms

# to incoporate node and edge information into the graph, with correponding color
for node in nodes[["Home","Name"]].to_numpy(): # this way of getting the values in the form of arrays is specific to Pandas DataFrame
    G_1.add_node(node[1],color=color_dict_1[node[0]])
for edge in edges[['Name1','Name2',"Relation"]].to_numpy():
    G_1.add_edge(edge[0],edge[1],color=color_dict_2[edge[2]])

# drawing the first graph via matplotlib
# names of the params are found in the documentation of networkx.draw_networkx()
nx.draw(G_1, with_labels=True,node_size=120,font_size=6,width=1.2,\
    node_color=list(nx.get_node_attributes(G_1,"color").values()),edge_color=list(nx.get_edge_attributes(G_1,"color").values()))
matplotlib.rcParams["font.sans-serif"]=["KaiTi"] 
# the above help find and show Chinese characters, many of which are absent from the lib without this declaration
plt.show()


# then we generate importance-correlation form
import math
# we could open the files in a for-loop using f-string, thanks to the deliberate naming
for i in range(1,5): # range(1,5) == [1,2,3,4]
    nodes=pd.read_csv(f"nodes_importances_part{i}.tsv",sep='\t')
    edges=pd.read_csv(f"edges_connections{i}.tsv",sep='\t')

    G_2=nx.Graph() 
    # the graph object will be re-created as an empty one for each file;
    # old graphs will be plotted in time before being replaced, so it's fine to overwritten

    # we would like to give an extra highlight to the nodes/edges which are significantly more important than others
    # borrowing an idea from the normal distribution: using standard deviation to decide "extreme objects"
    # not make perfect sense as this is not a normal distributed sample; but will be a good method for the objective anyway 
    avg1 = nodes["Importance"].mean()+2*nodes["Importance"].std()
    avg2 = edges["Connection"].mean()+2*edges["Connection"].std()

    # the range is huge, where max could be a thousand-fold greater than min 
    # must do some transformation to use the data as the reference for size/width
    # taking the log of the value turned out to be an ideal transformtion
    def size_function(value):
        # return math.ceil(500/(1+math.exp(-(value-avg1)/40))) 
        # the above was an old/self-designed way to constrain the size; abandoned as the log-function perfomrs well enough
        # saved only as a historical reference
        return 100*math.log(value)  # multiplied by 100, as the node size is by default 300.  
    def width_function(value):
        # return math.ceil(3.6/(1+math.exp(-(value-avg2)/20))) 
        # the same as above; may be useful if the values are even larger, e.g. up to millions
        return math.log(value)  # fortunately, log(value) falls in a reasonable range for width guidance; no need for more adjustaments

    for node in nodes[["Name", "Importance"]].to_numpy():
        if node[1]>avg1:    # to decide if the value is "extreme" with the help of the calculated avg1
            G_2.add_node(node[0], weight=size_function(node[1]),color="#55a2e9")    # darker blue 
        else:
            G_2.add_node(node[0], weight=size_function(node[1]),color="#9fc5e8")    # lighter blue  
    for edge in edges[['Name1','Name2',"Connection"]].to_numpy():
        if edge[2]>avg2:
            G_2.add_edge(edge[0],edge[1],weight=width_function(edge[2]),color="#696969")    # darker grey 
        else:
            G_2.add_edge(edge[0],edge[1],weight=width_function(edge[2]),color="#afafaf")    # lighter grey 

    # the following drawing performs similarly to the first one; the widths and sizes are defined accordingly though
    nx.draw(G_2, with_labels=True,font_size=6,width=list(nx.get_edge_attributes(G_2,"weight").values()), \
            edge_color=list(nx.get_edge_attributes(G_2,"color").values()),node_color=list(nx.get_node_attributes(G_2,"color").values()), \
            node_size=list(nx.get_node_attributes(G_2,"weight").values()))
    matplotlib.rcParams["font.sans-serif"]=["KaiTi"]
    plt.show()