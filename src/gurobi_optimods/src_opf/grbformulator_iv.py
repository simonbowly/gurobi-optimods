import logging
import gurobipy as gp
from gurobipy import GRB

from .grbformulator_ac import lpformulator_ac_create_efvars


def lpformulator_iv_body(alldata, model):
    """
    Adds variables and constraints for IV formulation to a given Gurobi model

    Parameters
    ----------
    alldata : dictionary
        Main dictionary holding all necessary data
    model : gurobipy.Model
        Gurobi model to be constructed
    """

    logger = logging.getLogger("OpfLogger")
    # Create model variables
    lpformulator_iv_create_vars(alldata, model)
    # Create model constraints
    lpformulator_iv_create_constraints(alldata, model)

    alldata["model"] = model


def lpformulator_iv_create_vars(alldata, model):
    """
    Creates and adds variables for IV formulation to a given Gurobi model

    Parameters
    ----------
    alldata : dictionary
        Main dictionary holding all necessary data
    model : gurobipy.Model
        Gurobi model to be constructed
    """

    logger = logging.getLogger("OpfLogger")
    logger.info("Creating variables.")

    fixtolerance = 1e-05

    if alldata["fixtolerance"] > 0:
        fixtolerance = alldata["fixtolerance"]

    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    IDtoCountmap = alldata["IDtoCountmap"]
    gens = alldata["gens"]

    # cffvars
    cffvar = {}

    varcount = 0

    """
    for j in range(1,numbuses+1):
        bus = buses[j]
        # First, injection variables
        maxprod = bus.Vmax*bus.Vmax
        minprod = bus.Vmin*bus.Vmin
        ubound  = maxprod
        lbound  = minprod

        if alldata['fixcs'] and bus.inputvoltage:
            lbound = bus.inputV*bus.inputV - fixtolerance
            ubound = bus.inputV*bus.inputV + fixtolerance

        cffvar[bus] = model.addVar(obj = 0.0, lb = lbound, ub = ubound,
                                 name = "cff_%d"%(bus.nodeID))

        varcount += 1

        #at this point, minprod is the square of bus min voltage

    logger.info('Added %d cff variables\n'%(varcount))
    """

    lpformulator_ac_create_efvars(alldata, model, varcount)

    # Next, generator variables
    GenPvar = {}
    GenQvar = {}

    for j in range(1, numbuses + 1):
        bus = buses[j]
        # First, injection variables
        maxprod = bus.Vmax * bus.Vmax
        minprod = bus.Vmin * bus.Vmin

        for genid in bus.genidsbycount:
            gen = gens[genid]
            lower = gen.Pmin * gen.status
            upper = gen.Pmax * gen.status
            # if bus.nodetype == 3:
            #  upper = GRB.INFINITY
            #  lower = -GRB.INFINITY  #ignoring slack bus
            GenPvar[gen] = model.addVar(
                obj=0.0, lb=lower, ub=upper, name="GP_%d_%d" % (gen.count, gen.nodeID)
            )
            varcount += 1

            lower = gen.Qmin * gen.status
            upper = gen.Qmax * gen.status
            if bus.nodetype == 3:
                lower = -GRB.INFINITY
                upper = GRB.INFINITY

            GenQvar[gen] = model.addVar(
                obj=0.0, lb=lower, ub=upper, name="GQ_%d_%d" % (gen.count, gen.nodeID)
            )
            varcount += 1

    logger.info("Added generator variables.")

    # Branch related variables
    branches = alldata["branches"]
    numbranches = alldata["numbranches"]

    irvar_f = {}  # branches!
    irvar_t = {}
    ijvar_f = {}  # branches!
    ijvar_t = {}

    Pvar_f = {}
    Qvar_f = {}
    Pvar_t = {}
    Qvar_t = {}

    if alldata["ivtype"] == "plain":
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            f = branch.f
            t = branch.t
            count_of_f = IDtoCountmap[f]
            count_of_t = IDtoCountmap[t]
            busf = buses[count_of_f]
            bust = buses[count_of_t]
            maxprod = buses[count_of_f].Vmax * buses[count_of_t].Vmax
            minprod = buses[count_of_f].Vmin * buses[count_of_t].Vmin
            if branch.constrainedflow:
                limit = branch.limit
            else:
                limit = 2 * (
                    abs(alldata["summaxgenP"]) + abs(alldata["summaxgenQ"])
                )  # Generous: assumes line charging up to 100%. However it still amounts to an assumption.

            ubound = 1e5  # 1 + np.sqrt(limit*limit/minprod ) #upper bound on current magnitude
            lbound = -ubound

            irvar_f[branch] = model.addVar(
                obj=0.0,
                lb=lbound,
                ub=ubound,
                name="ir_f_%d_%d_%d" % (j, busf.nodeID, bust.nodeID),
            )
            varcount += 1
            irvar_t[branch] = model.addVar(
                obj=0.0,
                lb=lbound,
                ub=ubound,
                name="ir_t_%d_%d_%d" % (j, bust.nodeID, busf.nodeID),
            )
            varcount += 1

            ijvar_f[branch] = model.addVar(
                obj=0.0,
                lb=lbound,
                ub=ubound,
                name="ij_f_%d_%d_%d" % (j, busf.nodeID, bust.nodeID),
            )
            varcount += 1
            ijvar_t[branch] = model.addVar(
                obj=0.0,
                lb=lbound,
                ub=ubound,
                name="ij_t_%d_%d_%d" % (j, bust.nodeID, busf.nodeID),
            )
            varcount += 1

        logger.info("Added branch current variables.")
    else:
        logger.info("Aggressive IV formulation, so skipping current variables.")

    for j in range(1, 1 + numbranches):
        branch = branches[j]
        f = branch.f
        t = branch.t
        count_of_f = IDtoCountmap[f]
        count_of_t = IDtoCountmap[t]
        busf = buses[count_of_f]
        bust = buses[count_of_t]
        if branch.constrainedflow:
            ubound = branch.limit
        else:
            ubound = 2 * (
                abs(alldata["summaxgenP"]) + abs(alldata["summaxgenQ"])
            )  # Generous: assumes line charging up to 100%. However it still amounts to an assumption.
        lbound = -ubound

        Pvar_f[branch] = model.addVar(
            obj=0.0,
            lb=lbound,
            ub=ubound,
            name="P_%d_%d_%d" % (j, busf.nodeID, bust.nodeID),
        )
        varcount += 1

        Pvar_t[branch] = model.addVar(
            obj=0.0,
            lb=lbound,
            ub=ubound,
            name="P_%d_%d_%d" % (j, bust.nodeID, busf.nodeID),
        )
        branch.Ptfvarind = varcount
        varcount += 1

        Qvar_f[branch] = model.addVar(
            obj=0.0,
            lb=lbound,
            ub=ubound,
            name="Q_%d_%d_%d" % (j, busf.nodeID, bust.nodeID),
        )
        varcount += 1

        Qvar_t[branch] = model.addVar(
            obj=0.0,
            lb=lbound,
            ub=ubound,
            name="Q_%d_%d_%d" % (j, bust.nodeID, busf.nodeID),
        )
        branch.Qtfvarind = varcount
        varcount += 1

    logger.info("Added branch power flow variables.")

    """
    #next, bus current variables
    #coarse bounds for now

    #commented out but will probably dump
    for j in range(1,numbuses+1):
        bus = buses[j]
        # First, injection variables
        ubound = 2*(abs(alldata['summaxgenP']) + abs(alldata['summaxgenQ']))/bus.Vmin
        #Generous: assumes all power routed through bus, and then some. However it still amounts to an assumption.
        irvar[bus] = model.addVar(obj = 0.0, lb = -ubound, ub = ubound,
                                    name = "ir_%d"%(busf.nodeID))
        bus.irvarind = varcount
        varcount += 1
        ijvar[bus] = model.addVar(obj = 0.0, lb = -ubound, ub = ubound,
                                    name = "ij_%d"%(busf.nodeID))
        bus.ijvarind = varcount
        varcount += 1

    logger.info('Added bus current variables.')
    """

    lincostvar = model.addVar(
        obj=1.0, lb=-GRB.INFINITY, ub=GRB.INFINITY, name="lincost"
    )
    alldata["LP"]["lincostvar"] = lincostvar
    alldata["LP"]["lincostvarind"] = varcount
    varcount += 1

    if alldata["usequadcostvar"]:
        quadcostvar = model.addVar(obj=1.0, lb=0, ub=GRB.INFINITY, name="quadcost")
        alldata["LP"]["quadcostvar"] = quadcostvar
        alldata["LP"]["quadcostvarind"] = varcount
        varcount += 1

    constobjval = 0
    for gen in gens.values():
        if gen.status > 0:
            constobjval += gen.costvector[gen.costdegree]

    constvar = model.addVar(obj=constobjval, lb=1.0, ub=1.0, name="constant")
    alldata["LP"]["constvar"] = constvar
    varcount += 1

    # Save variable data
    # alldata['LP']['cffvar']   = cffvar
    # alldata['LP']['irvar']   = irvar
    # alldata['LP']['ijvar']   = ijvar
    alldata["LP"]["irvar_f"] = irvar_f
    alldata["LP"]["irvar_t"] = irvar_t
    alldata["LP"]["ijvar_f"] = ijvar_f
    alldata["LP"]["ijvar_t"] = ijvar_t
    alldata["LP"]["Pvar_f"] = Pvar_f
    alldata["LP"]["Pvar_t"] = Pvar_t
    alldata["LP"]["Qvar_f"] = Qvar_f
    alldata["LP"]["Qvar_t"] = Qvar_t
    alldata["LP"]["GenPvar"] = GenPvar
    alldata["LP"]["GenQvar"] = GenQvar

    logger.info("Added a total of %d variables." % (varcount))


def lpformulator_iv_create_constraints(alldata, model):
    """
    Creates and adds constraints for IV formulation to a given Gurobi model
    TODO-Dan Is this function very different from the one in grbformulator_ac.py?
             Couldn't we call lpformulator_ac_create_constraints(alldata, model)
             and then add the missing IV constraints?

    Parameters
    ----------
    alldata : dictionary
        Main dictionary holding all necessary data
    model : gurobipy.Model
        Gurobi model to be constructed
    """

    logger = logging.getLogger("OpfLogger")
    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    numbranches = alldata["numbranches"]
    branches = alldata["branches"]
    gens = alldata["gens"]
    IDtoCountmap = alldata["IDtoCountmap"]
    evar = alldata["LP"]["evar"]
    fvar = alldata["LP"]["fvar"]
    # cffvar        = alldata['LP']['cffvar']
    # irvar        = alldata['LP']['irvar']
    # ijvar        = alldata['LP']['ijvar']
    irvar_f = alldata["LP"]["irvar_f"]
    irvar_t = alldata["LP"]["irvar_t"]
    ijvar_f = alldata["LP"]["ijvar_f"]
    ijvar_t = alldata["LP"]["ijvar_t"]
    Pvar_f = alldata["LP"]["Pvar_f"]
    Pvar_t = alldata["LP"]["Pvar_t"]
    Qvar_f = alldata["LP"]["Qvar_f"]
    Qvar_t = alldata["LP"]["Qvar_t"]

    GenPvar = alldata["LP"]["GenPvar"]
    GenQvar = alldata["LP"]["GenQvar"]
    lincostvar = alldata["LP"]["lincostvar"]

    logger.info("Creating constraints.")
    logger.info("  Adding cost definition.")

    coeff = [gen.costvector[gen.costdegree - 1] for gen in gens.values()]
    variables = [GenPvar[gen] for gen in gens.values()]
    expr = gp.LinExpr(coeff, variables)
    model.addConstr(expr == lincostvar, name="lincostdef")

    numquadgens = 0
    for gen in gens.values():
        if gen.costdegree >= 2 and gen.costvector[0] > 0 and gen.status:
            numquadgens += 1

    logger.info(
        "    Number of generators with quadratic cost coefficient: %d." % numquadgens
    )

    if numquadgens > 0:
        if alldata["usequadcostvar"]:
            quadcostvar = alldata["LP"]["quadcostvar"]
            logger.info("    Adding quadcost definition constraint.")
            qcost = gp.QuadExpr()
            for gen in gens.values():
                if gen.costdegree == 2 and gen.costvector[0] != 0:
                    qcost.add(gen.costvector[0] * GenPvar[gen] * GenPvar[gen])

            model.addConstr(qcost <= quadcostvar, name="qcostdef")
        else:
            logger.info("    Adding quad cost to objective.")
            model.update()  # Necessary to flush changes in the objective function
            oldobj = model.getObjective()
            newobj = gp.QuadExpr(oldobj)
            for gen in gens.values():
                if gen.costdegree == 2 and gen.costvector[0] != 0:
                    newobj.add(gen.costvector[0] * GenPvar[gen] * GenPvar[gen])

            model.setObjective(newobj, GRB.MINIMIZE)

    if alldata["ivtype"] == "plain":
        logger.info("  Adding branch current definitions.")
        # (g + jb)(e + jf) = g*e - b*f + j( b*e + g*f )
        count = 0
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            f = branch.f
            t = branch.t
            count_of_f = IDtoCountmap[f]
            count_of_t = IDtoCountmap[t]
            busf = buses[count_of_f]
            bust = buses[count_of_t]
            branch.Irfcname = "Irdef_%d_%d_%d" % (j, f, t)
            branch.Irtcname = "Irdef_%d_%d_%d" % (j, t, f)

            branch.Ijfcname = "Ijdef_%d_%d_%d" % (j, f, t)
            branch.Ijtcname = "Ijdef_%d_%d_%d" % (j, t, f)

            if branch.status:
                expr = (
                    branch.Gff * evar[busf]
                    - branch.Bff * fvar[busf]
                    + branch.Gft * evar[bust]
                    - branch.Bft * fvar[bust]
                )
            model.addConstr(expr == irvar_f[branch], name=branch.Irfcname)

            expr = (
                branch.Gtf * evar[busf]
                - branch.Btf * fvar[busf]
                + branch.Gtt * evar[bust]
                - branch.Btt * fvar[bust]
            )
            model.addConstr(expr == irvar_t[branch], name=branch.Irtcname)

            expr = (
                branch.Gff * fvar[busf]
                + branch.Bff * evar[busf]
                + branch.Gft * fvar[bust]
                + branch.Bft * evar[bust]
            )
            model.addConstr(expr == ijvar_f[branch], name=branch.Ijfcname)

            expr = (
                branch.Gtf * fvar[busf]
                + branch.Btf * evar[busf]
                + branch.Gtt * fvar[bust]
                + branch.Btt * evar[bust]
            )
            model.addConstr(expr == ijvar_t[branch], name=branch.Ijtcname)

            count += 4

        logger.info("    %d branch current definitions added." % count)

        logger.info("  Adding plain branch power definitions.")
        # (e + jf)*(Ir - jIj) = e*Ir + f*Ij + j( -e*Ij + f*Ir)
        count = 0
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            f = branch.f
            t = branch.t
            count_of_f = IDtoCountmap[f]
            count_of_t = IDtoCountmap[t]
            busf = buses[count_of_f]
            bust = buses[count_of_t]
            branch.Pfcname = "Pdef_%d_%d_%d" % (j, f, t)
            branch.Ptcname = "Pdef_%d_%d_%d" % (j, t, f)
            branch.Qfcname = "Qdef_%d_%d_%d" % (j, f, t)
            branch.Qtcname = "Qdef_%d_%d_%d" % (j, t, f)

            if branch.status:
                qexpr = evar[busf] * irvar_f[branch] + fvar[busf] * ijvar_f[branch]
                model.addConstr(qexpr == Pvar_f[branch], name=branch.Pfcname)

                qexpr = evar[bust] * irvar_t[branch] + fvar[bust] * ijvar_t[branch]
                model.addConstr(qexpr == Pvar_t[branch], name=branch.Ptcname)

                qexpr = -evar[busf] * ijvar_f[branch] + fvar[busf] * irvar_f[branch]
                model.addConstr(qexpr == Qvar_f[branch], name=branch.Qfcname)

                qexpr = -evar[bust] * ijvar_t[branch] + fvar[bust] * irvar_t[branch]
                model.addConstr(qexpr == Qvar_t[branch], name=branch.Qtcname)

            count += 4
        logger.info("    %d branch power flow definitions added." % count)
    else:
        logger.info(
            "Aggressive formulation, so will define power flows as functions of voltages."
        )

        logger.info("  Adding aggressive branch power definitions.")
        count = 0
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            f = branch.f
            t = branch.t
            count_of_f = IDtoCountmap[f]
            count_of_t = IDtoCountmap[t]
            busf = buses[count_of_f]
            bust = buses[count_of_t]
            branch.Pfcname = "Pdef_%d_%d_%d" % (j, f, t)
            branch.Ptcname = "Pdef_%d_%d_%d" % (j, t, f)
            branch.Qfcname = "Qdef_%d_%d_%d" % (j, f, t)
            branch.Qtcname = "Qdef_%d_%d_%d" % (j, t, f)

            if branch.status:
                gkk = branch.Gff
                bkk = branch.Bff
                gkm = branch.Gft
                bkm = branch.Bft

                # (e + jf)*(Ir - jIj) = e*Ir + f*Ij + j( -e*Ij + f*Ir)
                # But Ir = gkk*ek - bkk*fk + gkm*em - bkm*fm,
                # And Ij = bkk*ek + gkk*fk + bkm*em + gkm*fm

                # So real power from k to m = ek*[ gkk*ek - bkk*fk + gkm*em - bkm*fm ]
                #                           + fk*[ bkk*ek + gkk*fk + bkm*em + gkm*fm ] =
                #
                #                   gkk*(ek^2 + fk^2) + gkm*(ek*em + fk*fm) + bkm*(-ek*fm + em*fk)

                qexpr = gkk * (evar[busf] * evar[busf] + fvar[busf] * fvar[busf])
                qexpr += gkm * (evar[busf] * evar[bust] + fvar[busf] * fvar[bust])
                qexpr += bkm * (-evar[busf] * fvar[bust] + fvar[busf] * evar[bust])

                model.addConstr(qexpr == Pvar_f[branch], name=branch.Pfcname)

                # And imag power from k to m = -ek*[ bkk*ek + gkk*fk + bkm*em + gkm*fm ]
                #                            +  fk*[ gkk*ek - bkk*fk + gkm*em - bkm*fm ] =
                #
                #                 -bkk*(ek^2 + fk^2) - bkm*( ek*em + fk*fm) + gkm*(-ek*fm + em*fk)

                qexpr = -bkk * (evar[busf] * evar[busf] + fvar[busf] * fvar[busf])
                qexpr += -bkm * (evar[busf] * evar[bust] + fvar[busf] * fvar[bust])
                qexpr += gkm * (-evar[busf] * fvar[bust] + fvar[busf] * evar[bust])

                model.addConstr(qexpr == Qvar_f[branch], name=branch.Qfcname)

                # now, the reversals

                gmm = branch.Gtt
                bmm = branch.Btt
                gmk = branch.Gtf
                bmk = branch.Btf

                qexpr = gmm * (evar[bust] * evar[bust] + fvar[bust] * fvar[bust])
                qexpr += gmk * (evar[bust] * evar[busf] + fvar[bust] * fvar[busf])
                qexpr += bmk * (-evar[bust] * fvar[busf] + fvar[bust] * evar[busf])

                model.addConstr(qexpr == Pvar_t[branch], name=branch.Ptcname)

                qexpr = -bmm * (evar[bust] * evar[bust] + fvar[bust] * fvar[bust])
                qexpr += -bmk * (evar[bust] * evar[busf] + fvar[bust] * fvar[busf])
                qexpr += gmk * (-evar[bust] * fvar[busf] + fvar[bust] * evar[busf])

                model.addConstr(qexpr == Qvar_t[branch], name=branch.Qtcname)

                count += 4

        logger.info("    %d branch power flow definitions added." % count)

    # Balance constraints

    logger.info("  Adding active power balance constraints.")
    count = 0
    for j in range(1, 1 + numbuses):
        bus = buses[j]
        injpowerexpr = gp.LinExpr()
        for branchid in bus.frombranchids.values():
            injpowerexpr.add(Pvar_f[branches[branchid]])

        for branchid in bus.tobranchids.values():
            injpowerexpr.add(Pvar_t[branches[branchid]])

        genexpr = gp.LinExpr()
        if len(bus.genidsbycount) > 0:
            for genid in bus.genidsbycount:
                gen = gens[genid]
                genexpr.add(GenPvar[gen])

        model.addConstr(
            genexpr == injpowerexpr + bus.Pd, name="PBaldef%d_%d" % (j, bus.nodeID)
        )

        count += 1

    logger.info("    %d active bus power balance constraints added." % count)

    logger.info("  Adding reactive power balance constraints.")
    count = 0
    for j in range(1, 1 + numbuses):
        bus = buses[j]
        injpowerexpr = gp.LinExpr()
        for branchid in bus.frombranchids.values():
            injpowerexpr.add(Qvar_f[branches[branchid]])

        for branchid in bus.tobranchids.values():
            injpowerexpr.add(Qvar_t[branches[branchid]])

        genexpr = gp.LinExpr()
        if len(bus.genidsbycount) > 0:
            for genid in bus.genidsbycount:
                gen = gens[genid]
                genexpr.add(GenQvar[gen])

        model.addConstr(
            genexpr == injpowerexpr + bus.Qd, name="QBaldef%d_%d" % (j, bus.nodeID)
        )

        count += 1

    logger.info("    %d reactive bus power balance constraints added." % count)

    # the next set of constraints is optional
    """
    logger.info("  Adding constraints stating bus current injection = total outgoing current.")
    count = 0
    for j in range(1,1+numbuses):
        bus  = buses[j]
        expr = gp.LinExpr()

        if bus.Gs != 0:
            expr.add(bus.Gs*evar[bus])
        if bus.Bs != 0:
            expr.add(-bus.Bs*fvar[bus])

        if alldata['branchswitching_comp'] == False:
            for branchid in bus.frombranchids.values():
                expr.add(irvar_f[branches[branchid]])

            for branchid in bus.tobranchids.values():
                expr.add(irvar_t[branches[branchid]])
        model.addConstr(expr == irvar[bus], name = "IrBaldef%d_%d"%(j, bus.nodeID))

        count += 1

    for j in range(1,1+numbuses):
        bus  = buses[j]
        expr = gp.LinExpr()

        if bus.Gs != 0:
            expr.add(bus.Gs*fvar[bus])
        if bus.Bs != 0:
            expr.add(bus.Bs*evar[bus])

        if alldata['branchswitching_comp'] == False:
            for branchid in bus.frombranchids.values():
                expr.add(ijvar_f[branches[branchid]])

            for branchid in bus.tobranchids.values():
                expr.add(ijvar_t[branches[branchid]])
        model.addConstr(expr == ijvar[bus], name = "IrBaldef%d_%d"%(j, bus.nodeID))

        count += 1

    logger.info("    %d bus current balance constraints added."%count)
    """

    # Bus voltage limits.

    logger.info("  Adding voltage limits.")

    count = 0
    for j in range(1, 1 + numbuses):
        bus = buses[j]
        model.addConstr(
            evar[bus] ** 2 + fvar[bus] ** 2 <= bus.Vmax * bus.Vmax, name="Vmax_%d" % j
        )
        count += 1
        model.addConstr(
            evar[bus] ** 2 + fvar[bus] ** 2 >= bus.Vmin * bus.Vmin, name="Vmin_%d" % j
        )
        count += 1

    logger.info("    %d bus voltage limit constraints added." % count)

    # Branch limits.
    logger.info("  Adding branch limits.")
    count = 0
    for j in range(1, 1 + numbranches):
        branch = branches[j]

        if branch.status and branch.unboundedlimit == False:
            f = branch.f
            t = branch.t
            count_of_f = IDtoCountmap[f]
            count_of_t = IDtoCountmap[t]
            busf = buses[count_of_f]
            bust = buses[count_of_t]
            model.addConstr(
                Pvar_f[branch] * Pvar_f[branch] + Qvar_f[branch] * Qvar_f[branch]
                <= branch.limit**2,
                name="limit_f_%d_%d_%d" % (j, f, t),
            )
            # themodel.cbLazy(Pvar_t[branch]*Pvar_t[branch] + Qvar_t[branch]*Qvar_t[branch] <= branch.limit**2)
            model.addConstr(
                Pvar_t[branch] * Pvar_t[branch] + Qvar_t[branch] * Qvar_t[branch]
                <= branch.limit**2,
                name="limit_t_%d_%d_%d" % (j, t, f),
            )
            count += 2

    logger.info("    %d branch limits added." % count)

    # Active loss inequalities.
    if alldata["useactivelossineqs"] == True:
        logger.info("  Adding active loss constraints in weak form.")
        count = 0
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            if branch.status:
                f = branch.f
                t = branch.t
                count_of_f = IDtoCountmap[f]
                count_of_t = IDtoCountmap[t]
                busf = buses[count_of_f]
                bust = buses[count_of_t]

                model.addConstr(
                    Pvar_f[branch] + Pvar_t[branch] >= 0,
                    name="aLa_%d_%d_%d" % (j, f, t),
                )

                count += 1

        logger.info("    %d active loss inequalities added." % count)
