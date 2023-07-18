"""
Optimal Power Flow
------------------
"""

import logging

from gurobi_optimods.opf.grbcasereader import (
    convert_case_to_internal_format,
    read_case_file_mat,
    turn_opf_dict_into_mat_file,
)
from gurobi_optimods.opf.grbfile import (
    build_internal_settings,
    grbmap_volts_from_dict,
    read_file_csv,
)
from gurobi_optimods.opf.grbformulator import (
    compute_violations_from_voltages,
    construct_and_solve_model,
)
from gurobi_optimods.utils import optimod

logger = logging.getLogger(__name__)


@optimod()
def solve_opf_model(
    case,
    opftype="AC",
    branchswitching=False,
    minactivebranches=0.9,
    usemipstart=False,
    *,
    create_env,
):
    """
    Constructs an OPF model from given data and solves it with Gurobi. Returns a
    result dictionary following MATPOWER notation. The additional and possibly
    altered fields are

    - ``result["success"]`` 1 if at least one feasible solution has been found,
      0 otherwise
    - ``result["et"]`` time spent for optimization
    - ``result["f"]`` solution objective value
    - ``result["bus"][i]["Vm"]`` for voltage magnitude value at bus `i`
    - ``result["bus"][i]["Va"]`` for voltage angle value at bus `i`
    - ``result["bus"][i]["mu"]`` for shadow prices of balance constraints at bus
      `i` (only available for DC without branchswitching)
    - ``result["gen"][i]["Pg"]`` for real power injection at generator `i`
    - ``result["gen"][i]["Qg"]`` for reactive power injection at generator `i`
    - ``result["branch"][i]["Pf"]`` for real power injected into "from" end of
      branch at branch `i`
    - ``result["branch"][i]["Pt"]`` for real power injected into "to" end of
      branch at branch `i`
    - ``result["branch"][i]["Qf"]`` for reactive power injected into "from" end
      of branch at branch `i` (AC only)
    - ``result["branch"][i]["Qt"]`` for reactive power injected into "from" end
      of branch at branch `i` (AC only)
    - ``result["branch"][i]["switching"]`` states whether a branch `i` is turned
      on or off in the final solution

    Parameters
    ----------
    case : dict
        Dictionary holding case data
    opftype : str
        Desired OPF model type. One of ``AC``, ``AC_Relax``, ``DC``, or ``IV``.
    branchswitching : bool, optional
        If set to True, enables branch switching.
    minactivebranches : float, optional
        Defines the minimum number of branches that must be turned on when
        branch switching is active, i.e. the minimum number of turned on
        branches is equal to ``numbranches * min_active_branches``. Has no
        effect if ``branchswitching`` is set to False.
    usemipstart : bool, optional
        If set to True, try various MIP starts for branch switching models. Has
        no effect if ``branchswitching`` is set to False. For DC models, this
        setting is ignored, and the mip start is always used.
    valid_inequalities : str, optional
        Whether to include outer approximations for the AC formulation. Options
        are ``activeloss`` (the default), ``jabr``, or ``disable``. `jabr` uses
        SOCP constraints, ``activeloss`` uses linear outer approximations to the
        jabr inequalities, while ``disable`` does not generate valid
        inequalities.

    Returns
    -------
    dict
        Case dictionary following MATPOWER notation with additional result
        fields
    """

    # Exact cartesian AC
    if opftype.lower() == "ac":
        opftype = "ac"
        useef = True
        usejabr = True
        default_solver_params = {"MIPGap": 1e-3, "OptimalityTol": 1e-3}
    # AC relaxation using the JABR inequality
    elif opftype.lower() == "acrelax":
        opftype = "ac"
        useef = False
        usejabr = True
        default_solver_params = {"MIPGap": 1e-3, "OptimalityTol": 1e-3}
    # DC linear approximation
    elif opftype.lower() == "dc":
        opftype = "dc"
        useef = False
        usejabr = False
        default_solver_params = {"MIPGap": 1e-4, "OptimalityTol": 1e-4}
    else:
        raise ValueError(f"Unknown opftype '{opftype}'")

    with create_env(params=default_solver_params) as env:
        return _solve_opf_model_internal(
            env,
            case,
            opftype=opftype,
            useef=useef,
            usejabr=usejabr,
            branchswitching=branchswitching,
            usemipstart=usemipstart,
            minactivebranches=minactivebranches,
            polar=False,
            ivtype="aggressive",
            useactivelossineqs=False,
        )


def _solve_opf_model_internal(
    env,
    case,
    opftype,
    polar,
    useef,
    usejabr,
    ivtype,
    branchswitching,
    usemipstart,
    minactivebranches,
    useactivelossineqs,
):
    # Initialize settings dictionary
    settings = build_internal_settings(
        opftype,
        polar,
        useef,
        usejabr,
        ivtype,
        branchswitching,
        usemipstart,
        minactivebranches,
        useactivelossineqs,
    )

    # Populate the alldata dictionary with case data and settings
    alldata = convert_case_to_internal_format(case)
    alldata.update(settings)

    # Construct and solve model using given case data and user settings
    solution = construct_and_solve_model(env, alldata)

    return solution


@optimod()
def compute_violations_from_given_voltages(case, voltages, polar=False, *, create_env):
    """
    Constructs an OPF model from given case data and computes a violation dictionary
    out of given voltage values.

    If a voltage solution is present, e.g., from an external computation,
    this function can be used to check whether the given voltage solution is indeed
    feasible for the AC optimization model. Usually, if the violations are not too
    big, one can use the voltage solution for further calculations.

    Returns a violation dictionary following MATPOWER notation which holds
    all case data and additional violation fields. The additional fields are

    - ``violation["bus"][i]["Vmviol"]`` for voltage magnitude violation at bus `i`
    - ``violation["bus"][i]["Pviol"]`` for real injection violation at bus `i`
    - ``violation["bus"][i]["Qviol"]`` for reactive injection violation at bus `i`
    - ``violation["branch"][i]["limitviol"]`` for limit violation at branch `i`

    The violation dictionary can be used to generate a violations figure with the
    ``generate_opf_violations_figure`` function

    Parameters
    ----------
    case : dict
        Dictionary holding case data
    voltages : dict
        Dictionary holding bus input voltage data
    polar: bool, optional
        If True, use polar formulation when checking violations, defaults to False

    Returns
    -------
    dict
        Case dictionary following MATPOWER notation with additional violations fields

    """

    # Initialize fixed settings dictionary
    # We need the settings to construct a correct model
    settings = build_internal_settings(
        opftype="AC",
        polar=polar,
        useef=True,
        usejabr=False,
        ivtype="aggressive",
        branchswitching=0,
        usemipstart=False,
        useactivelossineqs=False,
        minactivebranches=0.95,
    )

    # Populate the alldata dictionary with case data and settings
    alldata = convert_case_to_internal_format(case)
    alldata.update(settings)

    # Map given voltage data to network data
    grbmap_volts_from_dict(alldata, voltages)

    # Compute model violations based on user input voltages
    with create_env() as env:
        violations = compute_violations_from_voltages(env, alldata)

    return violations


def read_case_from_mat_file(casefile):
    """
    Helper function for users.
    Reads a `.mat` data file and constructs a case dictionary,
    which can be used as input for other OPF API functions

    :param casefile: Name of and possibly full path to case file given as `.mat` file
                     The `.mat` file should be in standard MATPOWER notation
    :type casefile: str

    :return: Dictionary object of the given case which can be used in
             other OPF API functions
    :rtype: dict
    """

    case_dict = read_case_file_mat(casefile)

    return case_dict


def turn_result_into_mat_file(result, matfilename=""):
    """
    Writes a `.mat` data file in MATPOWER notation out of an OPF result dictionary.
    It accepts dictionaries in the format returned by the ``solve_opf_model`` and
    ``compute_violations_from_given_voltages`` functions

    :param result: OPF result dictionary
    :type result: dict
    :param matfilename: Name of `.mat` file where to write the result data,
                        defaults to `result.mat`
    :type matfilename: str, optional
    """

    # Set a default output file name
    if matfilename == "":
        matfilename = "result.mat"

    # Check for .mat suffix
    if not matfilename[-4:] == ".mat":
        matfilename += ".mat"
    logger.info(
        f"Generating .mat file {matfilename} out of given OPF result dictionary."
    )

    # Generate .mat file out of result
    turn_opf_dict_into_mat_file(result, matfilename)


def read_coords_from_csv_file(coordsfile):
    """
    Helper function for users.
    Constructs a coordinate dictionary which can be used as input
    for the ``generate_opf_solution_figure`` function.

    :param coordsfile: Name of and possibly full path to bus coordinates file given as `.csv` file.
                       The `.csv` file has to consist of the following columns in the given order:
                       ``index(starting with 0), busID, busname, latitude, longitude``
    :type coordsfile: str

    :return: Dictionary of the given coordinates which can be used in
             the ``generate_opf_solution_figure`` function
    :rtype: dict

    .. note::
        The first row of the csv file is ignored.
    """

    coord_dict = read_file_csv(coordsfile, "coordinates")

    return coord_dict


def read_voltages_from_csv_file(voltsfile):
    """
    Helper function for users.
    Constructs a bus input voltage dictionary which can be used as input
    for the ``check_voltage_solution_violations`` function

    :param voltsfile: Name of and possibly full path to voltage input file given as `.csv` file.
                       The `.csv` file has to consist of the following columns in the given order:
                       ``index(starting with 0), busID, busname, latitude, longitude``
    :type voltsfile: str

    :return: Dictionary of the given coordinates which can be used in
             the ``check_voltage_solution_violations`` function
    :rtype: dict

    .. note::
        The first row of the csv file is ignored.
    """

    volts_dict = read_file_csv(voltsfile, "voltages")

    return volts_dict
