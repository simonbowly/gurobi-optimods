# TODO: Facility Location OptiMod Implementation

## 1. Planning & Design

- [ ] Define the specific facility location problem variant (e.g., uncapacitated/capacitated, single/multiple allocation)
- [ ] Design the API interface (input/output formats)
- [ ] Decide on supported data formats (scipy sparse, pandas DataFrame, networkx, or custom)
- [ ] Plan example datasets and use cases

### Key Design Decisions
- **Problem variant**: Uncapacitated vs capacitated facility location
- **Input format**: Customer locations, facility candidate locations, costs (fixed + variable)
- **Output format**: Selected facilities, customer-to-facility assignments, total cost
- **Special features**: Multiple facilities per customer? Single-source or multi-source assignment?

## 2. Testing (TDD Approach) - `tests/test_facility_location.py`

- [ ] Create unit test file using `unittest` framework
- [ ] Write test for basic uncapacitated facility location with known solution
- [ ] Write test with scipy sparse matrix input
- [ ] Write test with pandas DataFrame input
- [ ] Write test with networkx graph input (if supported)
- [ ] Write test for small toy problems with known optimal solutions
- [ ] Write test for edge cases:
  - [ ] No feasible solution scenarios
  - [ ] Trivial solutions (single customer, single facility)
  - [ ] All facilities have zero fixed cost
  - [ ] Infinite capacity scenarios
- [ ] Write test for parameter validation and error handling:
  - [ ] Invalid data types
  - [ ] Mismatched dimensions
  - [ ] Negative costs
  - [ ] Empty inputs
- [ ] Write test with different solver parameters (verbose, logfile)
- [ ] Write test for capacitated facility location variant (if implementing)

## 3. Implementation - `src/gurobi_optimods/facility_location.py`

- [ ] Create the module file with proper header docstring
- [ ] Import required packages:
  - [ ] `import logging`
  - [ ] `import gurobipy as gp`
  - [ ] `from gurobipy import GRB`
  - [ ] `import numpy as np`
  - [ ] `import pandas as pd`
  - [ ] `import scipy.sparse as sp`
  - [ ] `from gurobi_optimods.utils import optimod`
  - [ ] Optional: `import networkx as nx` with try/except
- [ ] Set up logging: `logger = logging.getLogger(__name__)`
- [ ] Implement main function with `@optimod()` decorator signature
- [ ] Write complete numpydoc-style docstrings for the main function:
  - [ ] Description
  - [ ] Parameters section with types
  - [ ] Returns section with type
  - [ ] Examples section (optional, but helpful)
- [ ] Implement input validation and type checking
- [ ] Implement data preprocessing for different input formats:
  - [ ] Helper function for scipy sparse matrix format
  - [ ] Helper function for pandas DataFrame format
  - [ ] Helper function for networkx graph format (if supported)
- [ ] Build the optimization model:
  - [ ] Use `with create_env() as env, gp.Model(env=env) as model:` context manager
  - [ ] Create decision variables:
    - [ ] Binary variables for facility opening decisions
    - [ ] Variables for customer-to-facility assignments
  - [ ] Set objective function (minimize total cost: fixed + transportation)
  - [ ] Add constraints:
    - [ ] Each customer must be assigned to exactly one facility (or sufficient facilities)
    - [ ] Customers can only be assigned to open facilities
    - [ ] Capacity constraints (if capacitated variant)
  - [ ] Call `model.optimize()`
- [ ] Extract and post-process solution:
  - [ ] Extract which facilities are opened
  - [ ] Extract customer-to-facility assignments
  - [ ] Calculate total cost breakdown
- [ ] Return results in appropriate format matching input type
- [ ] Handle infeasible/unbounded cases gracefully
- [ ] Use `logger.info()` for any necessary output (e.g., solution summary)

## 4. Example Datasets (if needed)

- [ ] Create `src/gurobi_optimods/data/facility_location/` directory
- [ ] Create sample data files:
  - [ ] Small example (5-10 customers, 3-5 facilities) in CSV
  - [ ] Medium example with realistic costs
  - [ ] Geographic example with coordinates (optional)
- [ ] Implement `load_facility_location()` function in `datasets.py`:
  - [ ] Follow existing pattern (return `AttrDict`)
  - [ ] Load customer data
  - [ ] Load facility data
  - [ ] Load cost matrix or parameters to compute costs
- [ ] Add docstring to dataset loading function
- [ ] Test dataset loading works correctly

## 5. Documentation - `docs/source/mods/facility-location.rst`

- [ ] Create documentation file following existing mod structure
- [ ] Write introduction section:
  - [ ] Explain the facility location problem in plain language
  - [ ] Provide motivating real-world examples (warehouses, hospitals, servers, etc.)
  - [ ] Include a simple diagram or figure illustrating the problem
- [ ] Write "Problem Specification" section:
  - [ ] Define the problem formally with mathematical notation
  - [ ] Describe inputs (customers, facilities, costs)
  - [ ] Describe outputs (selected facilities, assignments)
  - [ ] Define objective clearly
- [ ] Write "Background: Mathematical Model" section inside `.. dropdown::` directive:
  - [ ] Define decision variables mathematically
  - [ ] Write objective function with mathematical notation
  - [ ] List all constraints with mathematical notation
  - [ ] Explain integrality/binary requirements
  - [ ] Optional: mention variants (capacitated, p-median, etc.)
  - [ ] Add references to classical facility location literature
- [ ] Write "Interface" section:
  - [ ] Use `.. tabs::` directive for different input formats
  - [ ] For each format (scipy/pandas/networkx):
    - [ ] Write `.. testcode::` block with complete runnable example
    - [ ] Write `.. testoutput::` block showing expected output
    - [ ] Explain the structure of inputs and outputs
  - [ ] Show how to interpret results
  - [ ] Show how to extract facility locations and assignments
- [ ] Create or include visualization:
  - [ ] Diagram showing problem setup (customers and candidate facilities)
  - [ ] Diagram showing optimal solution (selected facilities and assignments)
  - [ ] Save figures in `docs/source/mods/figures/`
- [ ] Add example with loaded dataset (if implemented)
- [ ] Document any optional parameters
- [ ] Add "See Also" or "References" section with relevant papers/books

## 6. Gallery & API Integration

- [ ] Add autodoc reference to `docs/source/api.rst`:
  ```rst
  .. automodule:: gurobi_optimods.facility_location
     :members: solve_facility_location
  ```
- [ ] Add gallery card to `docs/source/gallery.rst`:
  - [ ] Use `.. grid-item-card::` directive
  - [ ] Add descriptive title (e.g., "Facility Location")
  - [ ] Link to documentation: `:link: mods/facility-location`
  - [ ] Add icon/thumbnail: `:img-top: mods/icons/facility-location.png`
- [ ] Create or select an appropriate icon/figure for gallery card
- [ ] Place icon in `docs/source/mods/icons/` or use figure from `docs/source/mods/figures/`
- [ ] Ensure gallery card placement makes sense (alphabetical or by category)

## 7. Code Quality

- [ ] Run `pre-commit run --all-files` and fix any issues
- [ ] Run `python -m flake8 . --select=E9,F63,F7,F82,F811,F401 --show-source`
- [ ] Ensure code is formatted with black (should be automatic with pre-commit)
- [ ] Verify all docstrings follow numpydoc style guide
- [ ] Remove any unused imports or dead code
- [ ] Add type hints where appropriate
- [ ] Ensure consistent naming conventions
- [ ] Add comments only where necessary for clarification

## 8. Documentation Testing

- [ ] Build docs locally: `cd docs && make html` or `make livehtml`
- [ ] Verify documentation page renders correctly
- [ ] Run doctests: `make test` (includes doctests)
- [ ] Verify all `.. testcode::` blocks execute successfully
- [ ] Check all `.. testoutput::` blocks match actual output
- [ ] Verify math equations render properly (LaTeX)
- [ ] Check figures and images display correctly
- [ ] Ensure gallery card links to the correct page
- [ ] Test navigation between API reference and mod documentation

## 9. Final Testing

- [ ] Run full test suite: `make test`
- [ ] Ensure all unit tests pass
- [ ] Ensure all doctests pass
- [ ] Run tests with different Python versions (if possible)
- [ ] Test with minimal dependencies (optional imports)
- [ ] Verify code coverage for new module is adequate

## Notes

- Follow the existing patterns in other mods (e.g., `bipartite_matching.py`, `max_flow.py`)
- Keep the interface clean and user-friendly
- Shield users from direct gurobipy interaction
- Use context managers for all Gurobi objects
- Return results in the same format as input (scipy → scipy, pandas → pandas, etc.)
- Consider implementing both uncapacitated and capacitated variants
- Common variants to consider:
  - Uncapacitated Facility Location Problem (UFLP)
  - Capacitated Facility Location Problem (CFLP)
  - p-Median Problem (fixed number of facilities)
  - Fixed-Charge Facility Location
