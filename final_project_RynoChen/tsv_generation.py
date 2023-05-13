import re
import itertools

# the character list is saved as text file in advance
with open('characters.txt','r',encoding='utf-8') as rf:
    contents=rf.read()

home_dict={}    
# "hard-coding part"; 
# the contents of the list are segmented by homes, which is also what we want to do here
# the dictionary will have keys = which home, paired with values = all the contents in the corresponding sections
home_dict["神仙|Gods"]=re.match(r"(开头.+?)贾家",contents,re.DOTALL).group(1)
home_dict["贾家|Jia"]=re.search(r"(贾家.+?)史湘云的爷爷",contents,re.DOTALL).group(1)
home_dict["史家|Shi"]=re.search(r"(史家.+?)王熙凤的爷爷",contents,re.DOTALL).group(1)
home_dict["王家|Wang"]=re.search(r"(王家.+?)薛家的爷爷",contents,re.DOTALL).group(1)
home_dict["薛家|Xue"]=re.search(r"(薛家.+?)邢夫人家",contents,re.DOTALL).group(1)
home_dict["其他|Others"]=re.search(r"邢夫人家(.+)",contents,re.DOTALL).group(1)

# noticing the list denotes the couples in a special way (name1×name2), 
# we would like to extract them separately 
couples=[]

characters_dict={}  # character dict, intended key=home_name, val=char_set
characters=set()       # character set including everyone without any duplication; as a summary

for char_home, char_content in home_dict.items():       
    # to create a set containing all the names of the character
    # the regex works as in the list, each name is given in an individual line
    characters_mix=re.findall(r'\n(.+?)（', char_content)   # return a list
    characters_dict[char_home]=set() # to initialize the set, to avoid duplication
    for character in characters_mix:    # character is either a name or a couple
        if "×" in character:    # in case it's couple
            couples.append(character)   
            # relationship: couple, with each element being a string in the form "name1×name2";
            # could have more than 2 terms, husband × wifes
            
            # a character could appear twice, one individually with one as in couple 
            # so the condition "if char not in characters" is added in case the same name appears twice in different family sets
            # used method set.update to get each element from the list
            characters_dict[char_home].update([char for char in character.split("×") if char not in characters])
            characters.update(character.split("×")) # as characters is a set, no need for extra operations to avoid duplication
        else:   # similar operations as above
            if character not in characters:
                characters_dict[char_home].add(character)
                characters.add(character)


# in the following codes, we want another list including more relationships

# in the character list, a brief introduction is given after each name 
# in the form of "name1 (name2's someone)", ends with either ， or ）,using [，）]
# we use this as the regex
relation_reg=re.compile(r'\n(.+?)（(.+?)的(.+?)[，）]')
relationship_list=[]
relationships=relation_reg.findall(contents)
# some characters are named by "name's someone", we also grab their relationships
# as both tuple and list are indexable, it's fine to add the relationship as a list 
relationships+=[ [character]+character.split("的") for character in characters if "的" in character]

for relationship in relationships:  # valid relationship's form = name1, name2, relationship
    if relationship[0] in characters and relationship[1] in characters: # check if the form is correct
        if re.search(r"[妹姐哥兄弟]",relationship[2]):
            relation='Cousins'
        elif re.search(r'[女子胎]',relationship[2]):
            relation='Son|Daughter'
        elif re.search(r'[父母爷]',relationship[2]):
            relation='Parent'
        elif re.search(r'[妾陪房]',relationship[2]):
            relation='Couple'          # will be taken as the same with pairs in "couples" list
        elif re.search(r'[丫鬟小厮]',relationship[2]):
            relation='Servant'
        else:   # other relationships are not distinguished for here
            relation='Others'
        relation_str=str(relationship[0])+'\t'+str(relationship[1])+'\t'+relation   # create the tsv line
        relationship_list.append(relation_str)  # a list containing every line for the form
# also adding the information from the list couples into the relationship_list
for couple in couples:
    couple=couple.split("×")    # return a list
    relation_str=couple[0]+'\t'+couple[1]+'\t'+'Couple'
    relationship_list.append(relation_str)

# we then generate the node_list (characters & homes) and the edge_list (relationships)
with open("nodes_relationships.tsv",'w',encoding='utf-8') as wf:
    wf.write('Home'+'\t'+'Name')    # the "header"
    for home,character in characters_dict.items():  # home is a string, while character is a name set
        for char in character:
            wf.write(f'\n{home}\t{char}')
with open("edges_relationships.tsv",'w',encoding='utf-8') as wf:
    wf.write("Name1"+'\t'+'Name2'+'\t'+"Relation\n")    # the "header"
    wf.write('\n'.join(relationship_list))  # a list for all the lines is pre-generated


# we then work on the importance of characters

# will need character list we have generated, together with the original text we've saved in the files 
# we will have 4 forms of this in total: segment the story into 3 parts; 1 form for each + 1 for total
part_1=range(1,18)  # Ch 1-17
part_2=range(18,54)  # Ch 18-53
part_3=range(54,81)  # Ch 54-80
parts=[part_1,part_2,part_3]

# the first names of several important characters always appear alone
# we replace the first name with the full name to avoid missing them when counting
name_dict={}    # include all the name we need to transform, {first_name: full_name}
for character in characters:
    if character[0] in ["贾","王","史","薛","林",'秦',"傅","李"]:   # some common last names in the name list
        name_dict[character[1:]]=character
# creating a related regex
character_regex=""
for character in characters:
    character_regex+=character+'|'
character_regex=re.compile(character_regex[:-1])    # take [:-1], as the last element is '|'

# extracting information as the following 
# create 3 sub-dictionary and a total_dict (NO.4); each as an element in a "whole_dict"
connection={4:{}}   # for edges
importance={4:{}}   # for nodes
index=0 # index for sections
for part in parts:     
    index+=1
    sub_connect={}  # a local storage for the connections
    sub_importance={}   # a local storage for the importance statistics
    for i in part:    
        with open(f'{i}.txt','r',encoding='utf-8') as rf:
            contents=rf.read()
        for name, fname in name_dict.items():   # fname for full_name
            contents=re.sub(name,fname,contents)    # replace all the first name with full names to ensure the counting process
        # then to find the frequency of each names & how often they appear in pairs
        sentences=contents.split('。')
        # treat each sentence individually, as we define the connection by the frequency of names appearing in the same sentence
        for sentence in sentences:
            if character_regex.search(sentence):    # only when some names are mentioned in a sentence
                combo=character_regex.findall(sentence)
                for char in combo:
                    if char not in sub_importance.keys():   # create the pair for the first time
                        sub_importance[char]=0
                    sub_importance[char]+=1      # add one for each appearance
                    if char not in importance[4].keys():  # add to the total_dict simultaneously
                        importance[4][char]=0
                    importance[4][char]+=1
                combo=set(combo)    # in case a character appears in a sentence for more than 1 time
                pairs = list(itertools.combinations(combo, 2))
                for pair in pairs:      # pair is a tuple, whic is hashable and can be a key
                    if pair not in sub_connect.keys():   # create the pair for the first time
                        sub_connect[pair]=0
                    sub_connect[pair]+=1
                    if pair not in connection[4].keys():    # the same with importance
                        connection[4][pair]=0
                    connection[4][pair]+=1
        importance[index]=sub_importance     # to copy the local dictionary into the whole record
        connection[index]=sub_connect       


# then generate the second tsv
# with node (name & importance) and edges (relation & the strength)
for index in range(1,5):    # so that the forms for graphs[1,4] can be generated together  
    with open(f"nodes_importances_part{index}.tsv",'w',encoding='utf-8') as wf:
        wf.write('Name'+'\t'+'Importance')  # tsv form, separated by '\t'
        for character,significance in importance[index].items():     # importance[index], keys=name,val=imoprtance
            wf.write(f'\n{character}\t{significance}')  # tsv form, separated by '\t'
    with open(f"edges_connections{index}.tsv",'w',encoding='utf-8') as wf:
        wf.write("Name1"+'\t'+'Name2'+'\t'+"Connection")
        for pair,strength in connection[index].items():     # connection[index], keys=(name1,name2),val=strength
            wf.write(f'\n{pair[0]}\t{pair[1]}\t{strength}')
