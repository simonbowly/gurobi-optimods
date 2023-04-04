import sys
import os
import time
import math
import csv
import logging
import numpy as np

from .utils import get_default_optimization_settings, get_default_graphics_settings


def initialize_data_dict(logfile=""):

    alldata = {}
    alldata["LP"] = {}
    alldata["MIP"] = {}
    alldata["logfile"] = logfile

    return alldata


def read_optimization_settings(alldata, settings, casefile):

    # Currently Hard-coded
    alldata["usequadcostvar"] = False  # TODO-Dan What do we want to do with this?

    # TODO revisit default settings
    defaults = get_default_optimization_settings(casefile)
    # TODO get rid of this if-clause
    if type(settings) is dict:
        read_settings_dict(alldata, settings, casefile, defaults)
    else:
        read_settings_file(alldata, settings, casefile, defaults)

    if alldata["doslp_polar"] and (int(alldata["dodc"]) + int(alldata["doiv"]) == 0):
        alldata["doac"] = True

    if int(alldata["doac"]) + int(alldata["dodc"]) + int(alldata["doiv"]) != 1:
        raise ValueError(
            "Illegal option combination. Have to use exactly 1 of options [doac, dodc, doiv]."
        )


def read_graphics_settings(alldata, settings, casefile):

    # TODO revisit default settings
    defaults = get_default_graphics_settings(casefile)
    # TODO get rid of this if-clause
    if type(settings) is dict:
        read_settings_dict(alldata, settings, casefile, defaults)
    else:
        read_settings_file(alldata, settings, casefile, defaults)


def read_settings_dict(alldata, settings, casefile, defaults):
    """Sets settings in alldata from a settings dict"""

    for s in settings.keys():
        if s not in defaults.keys():
            raise ValueError("Illegal option string %s." % s)
        # Possible TODO do we have to check for correct types of values settings[s]?
        defaults[s] = settings[s]

    for s in defaults.keys():
        alldata[s] = defaults[s]


def read_settings_file(alldata, filename, casefile, settings):
    """Function to read configurations for OPF solve from config file"""

    logger = logging.getLogger("OpfLogger")
    logger.info("Reading configuration file %s." % filename)
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    linenum = 0
    # Read lines of configuration file and save options
    while linenum < len(lines):
        thisline = lines[linenum].split()

        if len(thisline) <= 0:
            linenum += 1
            continue

        if thisline[0][0] == "#":
            linenum += 1
            continue

        if thisline[0] == "END":
            break

        if thisline[0] not in settings.keys():
            raise ValueError("Illegal option string %s." % thisline[0])

        if len(thisline) > 2 and thisline[0] not in [
            "voltsfilename",
            "usevoltsolution",
        ]:
            raise ValueError("Illegal option string %s." % thisline[3])

        if len(thisline) == 2:
            settings[thisline[0]] = thisline[1]

        elif len(thisline) == 1:
            settings[thisline[0]] = True

        # handle special settings
        if thisline[0] == "usemaxdispersion":
            settings["usemaxdispersion"] = True
            if len(thisline) > 1:
                settings["maxdispersion_deg"] = float(thisline[1])

        elif thisline[0] == "usemaxphasediff":
            settings["usemaxphasediff"] = True
            if len(thisline) > 1:
                settings["maxphasediff_deg"] = float(thisline[1])

        elif thisline[0] == "strictcheckvoltagesolution":
            settings["strictcheckvoltagesolution"] = True
            if len(thisline) > 1:
                settings["voltsfilename"] = thisline[1]

        elif thisline[0] == "voltsfilename":
            if len(thisline) < 3:
                raise ValueError(
                    "Voltsfilename option requires filename and tolerance."
                )

            if settings["usevoltsolution"]:
                logging.error(
                    "Cannot use options voltsfilename and voltsolution at the same time."
                )
                raise ValueError(
                    "Illegal option combination. Cannot use both options voltsfilename and voltsolution."
                )

            settings["voltsfilename"] = thisline[1]
            settings["fixtolerance"] = float(thisline[2])

        elif thisline[0] == "usevoltsolution":
            if settings["voltsfilename"] != None:
                logging.error(
                    "Cannot use options voltsfilename and voltsolution at the same time."
                )
                raise ValueError(
                    "Illegal option combination. Cannot use both voltsfilename and voltsolution."
                )

            settings["usevoltsolution"] = True  # forcing solution in casefile

        elif thisline[0] == "useconvexformulation":
            settings["useconvexformulation"] = True
            settings["doac"] = True

        elif thisline[0] == "doiv":
            settings["doiv"] = True
            settings["use_ef"] = True  # needed
            if len(thisline) > 1:
                settings["ivtype"] = thisline[1]

        elif thisline[0] == "dographics":
            settings["dographics"] = True
            if len(thisline) > 1:
                settings["graphattrsfilename"] = thisline[1]

        linenum += 1

    logger.info("Settings:")
    for s in settings.keys():
        alldata[s] = settings[s]
        logger.info("  {} {}".format(s, settings[s]))

    logger.info("")


def grbread_graphattrs(alldata, filename):
    """Function to read graphical attributes"""

    logger = logging.getLogger("OpfLogger")
    logger.info("Reading graphical attributes file %s." % filename)
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    numfeatures = 0

    thresh = {}
    colorstring = {}
    sizeval = {}

    linenum = 0
    # Read lines of configuration file and save options
    while linenum < len(lines):
        thisline = lines[linenum].split()

        if len(thisline) <= 0:
            linenum += 1
            continue

        if thisline[0] == "END":
            break

        thresh[numfeatures] = int(thisline[0])
        colorstring[numfeatures] = thisline[1]
        sizeval[numfeatures] = int(thisline[2])
        numfeatures += 1

        linenum += 1

    logger.info("Read %d graphical features." % numfeatures)
    alldata["graphical"]["numfeatures"] = numfeatures
    alldata["graphical"]["thresh"] = thresh
    alldata["graphical"]["colorstring"] = colorstring
    alldata["graphical"]["sizeval"] = sizeval


def grbread_coords(alldata):
    """Reads csv file with bus coordinates"""

    logger = logging.getLogger("OpfLogger")
    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    IDtoCountmap = alldata["IDtoCountmap"]

    filename = alldata["coordsfilename"]
    logger.info("Reading csv coordinates file %s." % filename)

    f = open(filename, "r")
    csvf = csv.reader(f)
    thelist = list(csvf)
    f.close()

    for line in range(1, len(thelist)):
        # print(thelist[line][0], float(thelist[line][3]), float(thelist[line][4]))
        buses[line].lat = float(thelist[line][3])
        buses[line].lon = float(thelist[line][4])


def grbreadvoltsfile(alldata):
    """TODO-Dan add description"""

    logger = logging.getLogger("OpfLogger")
    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    IDtoCountmap = alldata["IDtoCountmap"]

    filename = alldata["voltsfilename"]
    logger.info("reading volts file %s." % filename)

    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    linenum = 0

    while linenum < len(lines):
        thisline = lines[linenum].split()
        if len(thisline) > 0:

            if thisline[0] == "END":
                break
            elif thisline[0] == "bus":
                busid = int(thisline[1])
                buscount = IDtoCountmap[busid]

                vm = float(thisline[3])
                vadeg = float(thisline[5])
                varad = vadeg * math.pi / 180.0

                buses[buscount].inputvoltage = 1
                buses[buscount].inputV = vm
                buses[buscount].inputA_rad = varad
            else:
                raise ValueError(
                    "Illegal line %d in voltsfile %s." % (linenum + 1, filename)
                )

        linenum += 1

    logger.info("Read volts file.\n")