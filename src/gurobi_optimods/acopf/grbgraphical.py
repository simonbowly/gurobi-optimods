import sys
import math
import time
from graph4 import *
#from log import Logger
from gurobipy import *
from myutils import break_exit

def grbgraphical(alldata, plottype):
    log         = alldata['log']
    buses       = alldata['buses']
    numbuses    = alldata['numbuses']
    branches    = alldata['branches']    
    numbranches = alldata['numbranches']
    gvfilename  = 'grbgraphical.gv'
    IDtoCountmap = alldata['IDtoCountmap']    
    txtfilename = 'newgraph.txt'
    log.joint("Graphical layout, 2\n")

    try:
        f = open(gvfilename, "w")
        log.joint("Writing to gv file %s\n"%gvfilename)
    except:
        log.raise_exception("Error: Cannot open file %s\n"%gvfilename)

    try:
        g = open(txtfilename, "w")
        log.joint("Writing to txt file %s\n"%txtfilename)
    except:
        log.raise_exception("Error: Cannot open file %s\n"%txtfilename)

    f.write("graph {\n")
    f.write('node [color=black, height=0, label=\"\\N\", shape=point, width=0];\n')
    g.write('N '+str(numbuses) + ' M ' + str(numbranches) + '\n')
    for bus in alldata['buses'].values():
        #f.write("     " + str(bus.nodeID)+";\n")
        f.write("     " + str(bus.count)+";\n")
    for branch in alldata['branches'].values():
        f.write("     " + str(branch.count_f)+" -- " + str(branch.count_t)+";\n")
        g.write(' ' + str(branch.count_f)+ ' ' + str(branch.count_t)+ '\n')

    f.write("}\n")
    f.close()
    g.write('END\n')
    g.close()

    scale       = 10
    firstgvfile = 'first.gv'
    sfdpcommand = 'sfdp -Goverlap_scaling='+str(scale)+' -o '+firstgvfile + ' ' + gvfilename
    log.joint('sfdp command: ' + sfdpcommand + '\n')
    system(sfdpcommand)

    '''
    jpgfile = 'second.jpg'
    neatocommand = 'neato -Tjpeg -n -o '+ jpgfile + ' ' + firstgvfile
    log.joint('neato command: ' + neatocommand + '\n')
    system(neatocommand)
    '''

    #break_exit('graph,1')
    node_text = {}
    mynode_size = {}
    mynode_color = {}
    mynode_border_width = {}
    myedge_width = {}
    myedge_color = {}
    
    #default actions for branches
    for j in range(1,numbuses+1):
        bus = buses[j]
        mynode_size[j-1] = 1
        mynode_color[j-1] = 'black'
        mynode_border_width[j-1] = 1
    for j in range(1,numbranches+1):
            branch = alldata['branches'][j]
            myedge_width[j] = 1
            myedge_color[j] = 'black'

    
    if plottype == 'violation':
        Vmagviol = alldata['violation']['Vmagviol']
        IPviol = alldata['violation']['IPviol']
        IQviol = alldata['violation']['IQviol']
        branchlimitviol = alldata['violation']['branchlimit']



        for j in range(1,numbuses+1):
            bus = buses[j]
            #node_text[j-1] = 'Bus ' + str(j) + ' Vmagviol: '+ str(Vmagviol[bus]) + ' Pviol: '+ str(IPviol[bus]) + ' Qviol: '+ str(IQviol[bus])

            node_text[j-1] = 'Bus %d Vmagviol: %.3e Pviol %.3e Qviol %.3e'%(j, Vmagviol[bus], IPviol[bus],IQviol[bus])
            if abs(Vmagviol[bus]) > 1e-3 or abs(IPviol[bus]) > 1e-2 or abs(IQviol[bus]) > 1e-2:
                mynode_size[j-1] = 15
                mynode_color[j-1] = 'red'

        for j in range(1,numbranches+1):
            branch = alldata['branches'][j]
            if abs(branchlimitviol[branch]) > 1e-3:
                myedge_width[j] = 8
                myedge_color[j] = 'red'
            
    elif plottype == 'branchswitching':

        loud = False
        for j in range(1,numbuses+1):
            bus = buses[j]
            node_text[j-1] = 'Bus ' + str(j)

        zvar         = alldata['LP']['zvar']
        zholder      = alldata['MIP']['zholder']
        for j in range(1,1+numbranches):
            branch     = branches[j]
            f          = branch.f
            t          = branch.t
            count_of_f = IDtoCountmap[f]
            count_of_t = IDtoCountmap[t]
            
            #if zvar[branch].x < 0.5:  #turned off
            if zholder[j-1] < 0.5:  #turned off
                if loud:
                    log.joint('branch %d (%d, %d) has small x\n'%(j, branch.count_f, branch.count_t))
                myedge_width[j] = 8
                myedge_color[j] = 'blue'
        
                mynode_size[count_of_f-1] = 15
                mynode_color[count_of_f-1] = 'red'
                mynode_size[count_of_t-1] = 15
                mynode_color[count_of_t-1] = 'red'
                #print(count_of_f, count_of_t)

    myedge_ends = {}
    myedge_list_consolidated = {}
    myedge_degrees_consolidated = {}
                
    loud = False
    for j in range(1,numbranches+1):
            branch = alldata['branches'][j]
            myedge_ends[(branch.count_f, branch.count_t)] = j
            myedge_ends[(branch.count_t, branch.count_f)] = j        
            small = min(branch.count_f, branch.count_t)
            large = max(branch.count_f, branch.count_t)
            if (small, large) not in myedge_list_consolidated.keys():
                myedge_degrees_consolidated[(small, large)] = 1
                myedge_list_consolidated[(small, large)] = []
                myedge_list_consolidated[(small, large)].append(j)
                if loud:
                    log.joint(' --> line %d color %s creates my consolidated list for (%d,%d)\n'%(j,myedge_color[j],small, large))
            else:
                myedge_degrees_consolidated[(small, large)] += 1
                myedge_list_consolidated[(small, large)].append(j)
                if loud:
                    log.joint(' --> appended line %d color %s to my consolidated list for (%d,%d)\n'%(j,myedge_color[j],small, large))              

    #break_exit('cons')
                
    graphplot(alldata, txtfilename, firstgvfile, node_text, mynode_size, mynode_color, mynode_border_width, myedge_width, myedge_color, myedge_ends, myedge_list_consolidated, myedge_degrees_consolidated, numbranches)
    #break_exit('graph,2')
