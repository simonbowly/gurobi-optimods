# Icon Generation Instructions for OptiMods

This document outlines the plan for creating light and dark stylized icons for each mod in the OptiMods gallery.

## TODO List

### 1. Bipartite Matching
- **Concept**: Two sets of nodes (bipartite graph) with edges connecting them, highlighting a matching
- **Visual**: Two columns of circles/dots with selected connecting lines emphasized
- **Alt text**: "Bipartite graph with two sets of nodes connected by matching edges"
- Files: `bipartite-matching-light.png`, `bipartite-matching-dark.png`

### 2. LAD Regression
- **Concept**: Scatter plot with a robust regression line, showing resistance to outliers
- **Visual**: Data points with a fitted line, emphasizing L1 norm (absolute deviations)
- **Alt text**: "Scatter plot with regression line showing robust fitting to data with outliers"
- Files: `lad-regression-light.png`, `lad-regression-dark.png`

### 3. Line Optimization
- **Concept**: Network/transit map with selected routes/lines highlighted
- **Visual**: Abstract network graph with emphasized paths representing optimal lines
- **Alt text**: "Transportation network with highlighted optimal routes and connections"
- Files: `line-optimization-light.png`, `line-optimization-dark.png`

### 4. Max Flow / Min Cut
- **Concept**: Network with flow from source to sink, showing capacity constraints
- **Visual**: Directed graph with arrows showing flow direction and a cut separating source/sink
- **Alt text**: "Network flow diagram with source, sink, and minimum cut edges highlighted"
- Files: `max-flow-min-cut-light.png`, `max-flow-min-cut-dark.png`

### 5. Metro Map
- **Concept**: Schematic octilinear representation (like subway maps)
- **Visual**: Stylized metro-style map with horizontal, vertical, and diagonal lines
- **Alt text**: "Schematic metro map with octilinear lines at right angles and diagonals"
- Files: `metromap-light.png`, `metromap-dark.png`

### 6. Minimum-Cost Flow
- **Concept**: Network flow with costs on edges, showing optimal routing
- **Visual**: Directed network with weighted edges and highlighted optimal flow path
- **Alt text**: "Network diagram showing minimum-cost flow path with weighted edges"
- Files: `min-cost-flow-light.png`, `min-cost-flow-dark.png`

### 7. Maximum Weighted Independent Set/Clique
- **Concept**: Graph with highlighted independent set (no edges between selected nodes)
- **Visual**: Graph nodes with subset highlighted, showing independence/clique property
- **Alt text**: "Graph with highlighted independent set of non-adjacent nodes"
- Files: `mwis-light.png`, `mwis-dark.png`

### 8. Optimal Power Flow
- **Concept**: Electrical grid network with generators and loads
- **Visual**: Network nodes (buses) with power flow arrows and generator symbols
- **Alt text**: "Electrical power grid with generator nodes and transmission lines"
- Files: `opf-light.png`, `opf-dark.png`

### 9. Mean-Variance Portfolio
- **Concept**: Efficient frontier curve showing risk-return tradeoff
- **Visual**: Smooth curve in risk-return space with optimal portfolio point
- **Alt text**: "Efficient frontier curve showing risk-return tradeoff with optimal portfolio"
- Files: `portfolio-light.png`, `portfolio-dark.png`

### 10. QUBO (Quadratic Unconstrained Binary Optimization)
- **Concept**: Ising model with up and down spins showing binary optimization
- **Visual**: Grid of up arrows (↑) and down arrows (↓) representing spin states
- **Alt text**: "Grid of up and down arrows representing spin states in QUBO optimization"
- Files: `qubo-light.png`, `qubo-dark.png`

### 11. Maximum Sharpe Ratio
- **Concept**: Portfolio optimization maximizing risk-adjusted returns
- **Visual**: Similar to efficient frontier but highlighting the tangency/optimal Sharpe point
- **Alt text**: "Risk-return plot with tangency line showing maximum Sharpe ratio portfolio"
- Files: `sharpe-ratio-light.png`, `sharpe-ratio-dark.png`

### 12. Workforce Scheduling
- **Concept**: Calendar/schedule grid with worker assignments
- **Visual**: Matrix/grid showing worker-shift assignments over time
- **Alt text**: "Schedule grid showing worker assignments across multiple shifts and days"
- Files: `workforce-light.png`, `workforce-dark.png`

## Design Guidelines

### Light Theme
- Background: white or very light color
- Foreground: dark colors for visibility
- Accent colors: blues, greens, purples (professional palette)
- Line width: medium to thin

### Dark Theme
- Background: dark gray or near-black
- Foreground: light colors for visibility
- Accent colors: brighter versions of light theme colors
- Line width: slightly thicker for visibility on dark background

## Implementation Notes
- Use matplotlib for all figures
- Target size: 400x300 pixels or similar aspect ratio
- Keep designs simple and iconic
- Emphasize the mathematical/optimization concept
- Use consistent styling across all icons
