import unittest

from gurobi_optimods.opf import (
    solve_opf_model,
    plot_opf_solution,
    read_settings_from_file,
    read_coords_from_csv_file,
    read_case_from_file,
    read_case_from_mat_file,
)
from gurobi_optimods.datasets import (
    load_caseopf,
    load_caseopfmat,
    load_caseNYopf,
    load_opfdictcase,
    load_coordsfilepath,
    load_opfgraphicssettings,
    load_opfsettings,
    load_case9solution,
)


class TestOpf(unittest.TestCase):

    numcases = 5
    cases = ["9", "14", "57", "118", "300"]
    # DC test values
    objvals_dc = [5216.026607, 7642.591776, 41006.736942, 125947.881417, 706240.290695]
    Va_dc = [6.177764, 6.283185, 6.171413, 5.817455, -5.520424]
    Pg_dc = [134.377585, 38.032305, 81.931329, 0, 1.2724979]
    Pt_dc = [-0.562622, 0.699608, -0.1809715, -1.0295381, 0.2483]
    # AC test values
    objvals_ac = [5296.686204, 8081.187603]
    Vm_ac = [1.08662, 1.018801]
    Qg_ac = [0.031844, 32.114784]
    Qf_ac = [0.129656, -0.1267811]
    # AC relaxation test values
    objvals_acconv = [5296.66532, 8074.9102, 41710.3065, 129338.093, 718613.607]
    Pg_acconv = [89.803524, 194.796114, 142.58252, 24.518669, 0.030902]
    Pt_acconv = [-0.341774, -0.7123414, -0.299637, 0.2379936, 0.562152]

    # test simple is on purpose the same as test_acopf for now
    # will be removed in final version
    def test_simple(self):
        settings = {
            "doac": True,
            "skipjabr": False,
            "use_ef": True,
            "branchswitching_mip": True,
        }
        # load path to case file
        casefile = load_caseopfmat("9")
        # read case file and return a case dictionary
        case = read_case_from_mat_file(casefile)
        # solve opf model and return a solution and the final objective value
        solution, objval = solve_opf_model(settings, case, "OPF.log")
        # check whether the solution points looks correct
        self.assertTrue(solution is not None)
        self.assertTrue(objval is not None)

    # test a real data set for New York
    def test_NY(self):
        settings = {"dodc": True}
        # load path to case file
        casefile, casemat = load_caseNYopf()
        # read case file and return a case dictionary
        case = read_case_from_file(casefile)
        casemat = read_case_from_mat_file(casemat)
        # solve opf model and return a solution and the final objective value
        solution, objval = solve_opf_model(settings, case, "OPF.log")
        solutionmat, objvalmat = solve_opf_model(settings, casemat, "OPF.log")
        self.assertTrue(solution is not None)
        self.assertTrue(objval is not None)
        self.assertTrue(solutionmat is not None)
        self.assertTrue(objvalmat is not None)

        # objective values should be the same because it's the same data
        self.assertTrue(objval == objvalmat)

        # get path to csv file holding the coordinates for NY
        coordsfile = load_coordsfilepath("nybuses.csv")
        coords_dict = read_coords_from_csv_file(coordsfile)
        # plot the given solution
        plot_opf_solution({}, case, coords_dict, solution, objval)

    # test reading settings and case file from dicts
    def test_opfdicts(self):
        settings = {"branchswitching_mip": True, "doac": True}
        case = load_opfdictcase()
        solution, objval = solve_opf_model(settings, case)
        # check whether the solution point looks correct
        self.assertTrue(solution is not None)
        self.assertTrue(objval is not None)
        self.assertLess(abs(solution["f"] - 5296.665647261), 1e-4)
        self.assertLess(abs(solution["bus"][1]["Va"] - 1), 1e-4)
        self.assertLess(abs(solution["gen"][2]["Qg"] - 3.14366), 1e-4)
        self.assertLess(abs(solution["branch"][3]["Pt"] - 0.568647), 1e-4)

    # test reading settings and case file
    def test_settingsfromfile(self):
        settingsfile = load_opfsettings()
        settings = read_settings_from_file(settingsfile)
        case = load_opfdictcase()
        solution, objval = solve_opf_model(settings, case)
        # check whether the solution point looks correct
        self.assertTrue(solution is not None)
        self.assertTrue(objval is not None)
        self.assertLess(abs(solution["f"] - 5296.665647261), 1e-4)
        self.assertLess(abs(solution["bus"][1]["Va"] - 1), 1e-4)
        self.assertLess(abs(solution["gen"][2]["Qg"] - 3.14366), 1e-4)
        self.assertLess(abs(solution["branch"][3]["Pt"] - 0.568647), 1e-4)

    # test DC formulation
    def test_dcopf(self):
        # set settings
        settings = {"branchswitching_mip": True, "dodc": True}

        for i in range(self.numcases):
            # load path to case file in .m and .mat format
            casefile = load_caseopf(self.cases[i])
            casefilemat = load_caseopfmat(self.cases[i])
            # read case file in .m and .mat format and return a case dictionary
            case = read_case_from_file(casefile)
            casemat = read_case_from_mat_file(casefilemat)
            # solve opf models and return a solution and the final objective value
            solution, objval = solve_opf_model(settings, case)
            solutionmat, objvalmat = solve_opf_model(settings, casemat)
            # check whether the solution point looks correct
            self.assertTrue(solution is not None)
            self.assertTrue(objval is not None)
            self.assertTrue(solutionmat is not None)
            self.assertTrue(objvalmat is not None)
            self.assertLess(abs(solution["f"] - self.objvals_dc[i]), 1e-4)
            self.assertLess(abs(solutionmat["f"] - self.objvals_dc[i]), 1e-4)
            self.assertLess(abs(solution["bus"][1]["Va"] - self.Va_dc[i]), 1e-4)
            self.assertLess(abs(solutionmat["bus"][1]["Va"] - self.Va_dc[i]), 1e-4)
            self.assertLess(abs(solution["gen"][2]["Pg"] - self.Pg_dc[i]), 1e-4)
            self.assertLess(abs(solutionmat["gen"][2]["Pg"] - self.Pg_dc[i]), 1e-4)
            self.assertLess(abs(solution["branch"][3]["Pt"] - self.Pt_dc[i]), 1e-4)
            self.assertLess(abs(solutionmat["branch"][3]["Pt"] - self.Pt_dc[i]), 1e-4)
            # objective values should be the same because it's the same data and the model is linear
            # without (too much) symmetry
            self.assertLess(abs(objval - objvalmat), 1e-2)

    # test AC formulation
    def test_acopf(self):
        settings = {"doac": True, "use_ef": True}

        for i in range(2):
            # load path to case file in .m and .mat format
            casefile = load_caseopf(self.cases[i])
            casefilemat = load_caseopfmat(self.cases[i])
            # read case file in .m and .mat format and return a case dictionary
            case = read_case_from_file(casefile)
            casemat = read_case_from_mat_file(casefilemat)
            # solve opf models and return a solution and the final objective value
            solution, objval = solve_opf_model(settings, case)
            solutionmat, objvalmat = solve_opf_model(settings, casemat)
            # check whether the solution point looks correct
            self.assertTrue(solution is not None)
            self.assertTrue(objval is not None)
            self.assertTrue(solutionmat is not None)
            self.assertTrue(objvalmat is not None)
            self.assertLess(abs(solution["f"] - self.objvals_ac[i]), 1e-4)
            self.assertLess(abs(solutionmat["f"] - self.objvals_ac[i]), 1e-4)
            self.assertLess(abs(solution["bus"][3]["Vm"] - self.Vm_ac[i]), 1e-4)
            self.assertLess(abs(solutionmat["bus"][3]["Vm"] - self.Vm_ac[i]), 1e-4)
            self.assertLess(abs(solution["gen"][2]["Qg"] - self.Qg_ac[i]), 1e-4)
            self.assertLess(abs(solutionmat["gen"][2]["Qg"] - self.Qg_ac[i]), 1e-4)
            self.assertLess(abs(solution["branch"][1]["Qf"] - self.Qf_ac[i]), 1e-4)
            self.assertLess(abs(solutionmat["branch"][1]["Qf"] - self.Qf_ac[i]), 1e-4)

            # objective value should be the same because it's the same data
            self.assertLess(abs(objval - objvalmat), 1e-2)
            # cannot check solution point because it can be symmetric

    # test AC formulation relaxation
    def test_acopfconvex(self):
        settings = {"doac": True}

        for i in range(self.numcases):
            # load path to case file in .m and .mat format
            casefile = load_caseopf(self.cases[i])
            casefilemat = load_caseopfmat(self.cases[i])
            # read case file in .m and .mat format and return a case dictionary
            case = read_case_from_file(casefile)
            casemat = read_case_from_mat_file(casefilemat)
            # solve opf models and return a solution and the final objective value
            solution, objval = solve_opf_model(settings, case)
            solutionmat, objvalmat = solve_opf_model(settings, casemat)
            # check whether the solution point looks correct
            self.assertTrue(solution is not None)
            self.assertTrue(objval is not None)
            self.assertTrue(solutionmat is not None)
            self.assertTrue(objvalmat is not None)
            self.assertLess(abs(objval - self.objvals_acconv[i]), 1)
            self.assertLess(abs(solution["gen"][1]["Pg"] - self.Pg_acconv[i]), 1)
            self.assertLess(abs(solutionmat["gen"][1]["Pg"] - self.Pg_acconv[i]), 1)
            self.assertLess(abs(solution["branch"][2]["Pt"] - self.Pt_acconv[i]), 1)
            self.assertLess(abs(solutionmat["branch"][2]["Pt"] - self.Pt_acconv[i]), 1)

            # objective value should be the same because it's the same data
            # the bigger cases are numerically difficult with large obj vals and we are running Barrier
            # so there can be quite a difference in objective value
            if self.cases[i] == "300":
                # case 300 is quite large and has numerical issues
                self.assertLess(abs(objval - objvalmat), 100)
            else:
                self.assertLess(abs(objval - objvalmat), 1)

    # test IV formulation
    def test_ivopf(self):
        # set settings
        settings = {"doiv": True, "ivtype": "aggressive"}
        # load path to case file
        # currently all other cases take very long in IV formulation
        casefile = load_caseopf("9")
        # read case file and return a case dictionary
        case = read_case_from_file(casefile)
        # solve opf model and return a solution and the final objective value
        solution, objval = solve_opf_model(settings, case)
        # check whether the solution points looks correct
        self.assertTrue(solution is not None)
        self.assertTrue(objval is not None)
        self.assertLess(abs(solution["f"] - 5296.716652), 1e-4)
        # TODO finish test for IV
        # print(solution["bus"][3]["Vm"])
        # print(solution["gen"][2]["Qg"])
        # print(solution["branch"][1]["Qf"])

    # test plotting a solution from pre-loaded data
    def test_graphics(self):
        # settings dictionary
        graphics_settings = {}
        # get path to csv file holding the coordinates for case 9
        coordsfile = load_coordsfilepath("case9coords.csv")
        coords_dict = read_coords_from_csv_file(coordsfile)
        # load case dictionary
        case = load_opfdictcase()
        # load a precomputed solution and objective value
        solution, objval = load_case9solution()
        # plot the given solution
        plot_opf_solution(graphics_settings, case, coords_dict, solution, objval)

    # test plotting a solution after optimization is performed
    def test_graphics_after_solving(self):
        # load settings dictionary
        optimization_settings = {
            "doac": True,
            "use_ef": True,
            "branchswitching_mip": True,
        }
        # load case dictionary
        case = load_opfdictcase()
        # solve opf model and return a solution and the final objective value
        solution, objval = solve_opf_model(optimization_settings, case)
        # plot the computed solution
        # graphics_settings = {"branchswitching_mip": True}
        graphics_settings = {}
        coordsfile = load_coordsfilepath("case9coords.csv")
        coords_dict = read_coords_from_csv_file(coordsfile)
        plot_opf_solution(graphics_settings, case, coords_dict, solution, objval)

    # test plotting a solution while reading graphics settings from a file
    def test_graphics_settings_file(self):
        # load path to settings file
        settingsfile = load_opfgraphicssettings()
        # read settings file and return a settings dictionary
        # set second argument to True because it's a graphics settings file
        graphics_settings = read_settings_from_file(settingsfile, True)
        coordsfile = load_coordsfilepath("case9coords.csv")
        coords_dict = read_coords_from_csv_file(coordsfile)
        # load path to case file
        casefile = load_caseopf("9")
        # read case file and return a case dictionary
        case = read_case_from_file(casefile)
        # load a precomputed solution and objective value
        solution, objval = load_case9solution()
        # plot the computed solution
        plot_opf_solution(graphics_settings, case, coords_dict, solution, objval)
