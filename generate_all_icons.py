#!/usr/bin/env python3
"""
Generate stylized icons for OptiMods gallery.
Creates both light and dark theme versions of each icon.
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from gurobi_optimods.mwis import (
    maximum_weighted_clique,
    maximum_weighted_independent_set,
)

# Output directory
ICON_DIR = Path("docs/source/mods/icons")
ICON_DIR.mkdir(parents=True, exist_ok=True)

# Color schemes
LIGHT_THEME = {
    "bg": "none",
    "fg": "#2c3e50",
    "accent1": "#3498db",  # blue
    "accent2": "#2ecc71",  # green
    "accent3": "#9b59b6",  # purple
    "accent4": "#e74c3c",  # red
    "line_width": 2,
}

DARK_THEME = {
    "bg": "none",
    "fg": "#ecf0f1",
    "accent1": "#5dade2",  # lighter blue
    "accent2": "#58d68d",  # lighter green
    "accent3": "#af7ac5",  # lighter purple
    "accent4": "#ec7063",  # lighter red
    "line_width": 2.5,
}


def create_figure(theme):
    """Create a figure with the given theme."""
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    fig.patch.set_facecolor(theme["bg"])
    ax.set_facecolor(theme["bg"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    return fig, ax


def save_figure(fig, name, theme_name):
    """Save figure with proper naming."""
    filename = ICON_DIR / f"{name}-{theme_name}.png"
    fig.savefig(
        filename,
        dpi=100,
        bbox_inches="tight",
        facecolor="none",
        edgecolor="none",
        transparent=True,
    )
    plt.close(fig)
    print(f"✓ Created {filename}")


def bipartite_matching(theme, theme_name):
    """Bipartite graph with matching edges."""
    fig, ax = create_figure(theme)

    # Left set of nodes
    left_x = 2
    left_y = [2, 4, 6, 8]

    # Right set of nodes
    right_x = 8
    right_y = [2.5, 4.5, 6.5, 8.5]

    # All possible edges (light)
    for ly in left_y:
        for ry in right_y:
            ax.plot(
                [left_x, right_x], [ly, ry], color=theme["fg"], alpha=0.15, linewidth=1
            )

    # Matching edges (highlighted)
    matches = [(0, 1), (1, 2), (2, 3), (3, 0)]
    for l_idx, r_idx in matches:
        ax.plot(
            [left_x, right_x],
            [left_y[l_idx], right_y[r_idx]],
            color=theme["accent1"],
            linewidth=theme["line_width"],
            zorder=2,
        )

    # Nodes
    for ly in left_y:
        ax.scatter(
            left_x,
            ly,
            s=300,
            color=theme["accent2"],
            edgecolor=theme["fg"],
            linewidth=2,
            zorder=3,
        )
    for ry in right_y:
        ax.scatter(
            right_x,
            ry,
            s=300,
            color=theme["accent2"],
            edgecolor=theme["fg"],
            linewidth=2,
            zorder=3,
        )

    save_figure(fig, "bipartite-matching", theme_name)


def lad_regression(theme, theme_name):
    """Scatter plot with robust regression line."""
    fig, ax = create_figure(theme)

    # Generate data with outliers
    np.random.seed(42)
    x = np.linspace(1, 9, 15)
    y = 2 + 0.7 * x + np.random.normal(0, 0.5, len(x))

    # Add outliers
    y[3] += 3.5
    y[10] -= 3.0

    # Regression line
    line_x = np.array([1, 9])
    line_y = 2 + 0.7 * line_x
    ax.plot(
        line_x,
        line_y,
        color=theme["accent1"],
        linewidth=theme["line_width"],
        label="LAD fit",
        zorder=2,
    )

    # Data points
    ax.scatter(
        x,
        y,
        s=100,
        color=theme["accent2"],
        edgecolor=theme["fg"],
        linewidth=1.5,
        zorder=3,
        alpha=0.8,
    )

    # Highlight outliers
    ax.scatter(
        [x[3], x[10]],
        [y[3], y[10]],
        s=120,
        color=theme["accent4"],
        edgecolor=theme["fg"],
        linewidth=2,
        zorder=4,
        alpha=0.9,
    )

    save_figure(fig, "lad-regression", theme_name)


def line_optimization(theme, theme_name):
    """Transit network with optimal lines."""
    fig, ax = create_figure(theme)

    # Network nodes
    nodes = np.array(
        [
            [2, 2],
            [3, 5],
            [3, 8],
            [5, 3],
            [5, 6],
            [5, 9],
            [7, 2],
            [7, 5],
            [7, 8],
            [9, 4],
            [9, 7],
        ]
    )

    # All edges (light)
    edges = [
        (0, 3),
        (1, 2),
        (1, 4),
        (2, 5),
        (3, 6),
        (3, 4),
        (4, 5),
        (4, 7),
        (5, 8),
        (6, 9),
        (7, 8),
        (7, 9),
        (8, 10),
    ]
    for i, j in edges:
        ax.plot(
            [nodes[i, 0], nodes[j, 0]],
            [nodes[i, 1], nodes[j, 1]],
            color=theme["fg"],
            alpha=0.2,
            linewidth=2,
        )

    # Optimal lines (highlighted)
    line1 = [(0, 3), (3, 4), (4, 7), (7, 9)]
    line2 = [(1, 4), (4, 5), (5, 8)]

    for i, j in line1:
        ax.plot(
            [nodes[i, 0], nodes[j, 0]],
            [nodes[i, 1], nodes[j, 1]],
            color=theme["accent1"],
            linewidth=theme["line_width"] + 1,
            zorder=2,
            solid_capstyle="round",
        )

    for i, j in line2:
        ax.plot(
            [nodes[i, 0], nodes[j, 0]],
            [nodes[i, 1], nodes[j, 1]],
            color=theme["accent3"],
            linewidth=theme["line_width"] + 1,
            zorder=2,
            solid_capstyle="round",
        )

    # Nodes
    ax.scatter(
        nodes[:, 0],
        nodes[:, 1],
        s=200,
        color=theme["bg"],
        edgecolor=theme["fg"],
        linewidth=2,
        zorder=3,
    )

    save_figure(fig, "line-optimization", theme_name)


def max_flow_min_cut(theme, theme_name):
    """Network with flow and min cut."""
    fig, ax = create_figure(theme)

    # Nodes
    nodes = {
        "s": (1, 5),
        "a": (3, 7),
        "b": (3, 3),
        "c": (6, 7),
        "d": (6, 3),
        "t": (9, 5),
    }

    # Edges with flow
    edges = [
        ("s", "a"),
        ("s", "b"),
        ("a", "c"),
        ("b", "d"),
        ("c", "t"),
        ("d", "t"),
        ("a", "d"),
        ("b", "c"),
    ]

    # Draw edges
    for u, v in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="->", lw=theme["line_width"], color=theme["fg"], alpha=0.4
            ),
        )

    # Min cut edges (highlighted)
    cut_edges = [("a", "c"), ("b", "d")]
    for u, v in cut_edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        # Draw cut line
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot(
            [mid_x - 0.3, mid_x + 0.3],
            [mid_y - 0.3, mid_y + 0.3],
            color=theme["accent4"],
            linewidth=theme["line_width"] + 2,
            zorder=4,
            linestyle="--",
        )

    # Nodes
    for name, (x, y) in nodes.items():
        color = theme["accent1"] if name in ["s", "t"] else theme["accent2"]
        ax.scatter(
            x, y, s=400, color=color, edgecolor=theme["fg"], linewidth=2, zorder=3
        )
        ax.text(
            x,
            y,
            name,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=theme["bg"],
        )

    save_figure(fig, "max-flow-min-cut", theme_name)


def metromap(theme, theme_name):
    """Schematic metro map with octilinear lines using the metromap mod."""
    fig, ax = create_figure(theme)

    from gurobi_optimods import datasets
    from gurobi_optimods.metromap import metromap as metromap_solver

    # Load the reduced Berlin metro network
    graph_full, linepath_data_full = datasets.load_berlin_metro_reduced_graph_data()

    # Select only 2 lines to keep the problem small
    selected_lines = ["U1", "U2"]
    linepath_data = linepath_data_full[
        linepath_data_full["linename"].isin(selected_lines)
    ]

    # Get nodes used by these lines
    used_nodes = set(
        linepath_data["edge_source"].tolist() + linepath_data["edge_target"].tolist()
    )

    # Create subgraph with only these nodes
    graph = graph_full.subgraph(used_nodes).copy()

    # Compute metromap
    graph_out, edge_directions = metromap_solver(
        graph,
        linepath_data,
        penalty_line_bends=1,
        penalty_distance=1,
        penalty_edge_directions=1,
    )

    # Get the octilinear positions
    pos_oct = nx.get_node_attributes(graph_out, "pos_oct")

    # Scale positions to fit canvas
    if pos_oct:
        pos_array = np.array(list(pos_oct.values()))
        min_vals = pos_array.min(axis=0)
        max_vals = pos_array.max(axis=0)

        for node in pos_oct:
            x, y = pos_oct[node]
            pos_oct[node] = [
                1.5 + 7.0 * (x - min_vals[0]) / (max_vals[0] - min_vals[0]),
                1.5 + 7.0 * (y - min_vals[1]) / (max_vals[1] - min_vals[1]),
            ]

    # Define line colors for light and dark themes
    if theme_name == "light":
        line_colors = {
            "U1": "#3498db",  # blue
            "U2": "#e74c3c",  # red
        }
    else:  # dark theme
        line_colors = {
            "U1": "#5dade2",  # lighter blue
            "U2": "#ec7063",  # lighter red
        }

    # Draw edges grouped by line
    for line in selected_lines:
        line_edges = linepath_data[linepath_data["linename"] == line]
        for _, row in line_edges.iterrows():
            src, tgt = row["edge_source"], row["edge_target"]
            if src in pos_oct and tgt in pos_oct:
                ax.plot(
                    [pos_oct[src][0], pos_oct[tgt][0]],
                    [pos_oct[src][1], pos_oct[tgt][1]],
                    color=line_colors[line],
                    linewidth=theme["line_width"] + 1.5,
                    solid_capstyle="round",
                    zorder=1,
                    alpha=0.9,
                )

    # Draw stations
    for node in pos_oct:
        ax.scatter(
            pos_oct[node][0],
            pos_oct[node][1],
            s=150,
            color="white" if theme["bg"] == "none" else theme["bg"],
            edgecolor=theme["fg"],
            linewidth=1.5,
            zorder=2,
        )

    save_figure(fig, "metromap", theme_name)


def min_cost_flow(theme, theme_name):
    """Network with minimum-cost flow path."""
    fig, ax = create_figure(theme)

    # Nodes
    nodes = np.array(
        [[1, 5], [3, 7], [3, 3], [5, 8], [5, 5], [5, 2], [7, 7], [7, 3], [9, 5]]
    )

    # All edges (costs shown as thickness)
    edges = [
        (0, 1),
        (0, 2),
        (1, 3),
        (1, 4),
        (2, 4),
        (2, 5),
        (3, 6),
        (4, 6),
        (4, 7),
        (5, 7),
        (6, 8),
        (7, 8),
    ]

    for i, j in edges:
        ax.plot(
            [nodes[i, 0], nodes[j, 0]],
            [nodes[i, 1], nodes[j, 1]],
            color=theme["fg"],
            alpha=0.2,
            linewidth=2,
        )

    # Optimal flow path (highlighted)
    flow_path = [(0, 1), (1, 4), (4, 7), (7, 8)]
    for i, j in flow_path:
        ax.annotate(
            "",
            xy=(nodes[j, 0], nodes[j, 1]),
            xytext=(nodes[i, 0], nodes[i, 1]),
            arrowprops=dict(
                arrowstyle="->",
                lw=theme["line_width"] + 1,
                color=theme["accent1"],
                connectionstyle="arc3,rad=0",
            ),
        )

    # Nodes
    # Source and sink
    ax.scatter(
        nodes[0, 0],
        nodes[0, 1],
        s=400,
        color=theme["accent2"],
        edgecolor=theme["fg"],
        linewidth=2,
        zorder=3,
    )
    ax.scatter(
        nodes[8, 0],
        nodes[8, 1],
        s=400,
        color=theme["accent4"],
        edgecolor=theme["fg"],
        linewidth=2,
        zorder=3,
    )
    # Intermediate
    for i in range(1, 8):
        ax.scatter(
            nodes[i, 0],
            nodes[i, 1],
            s=250,
            color=theme["bg"],
            edgecolor=theme["fg"],
            linewidth=2,
            zorder=3,
        )

    save_figure(fig, "min-cost-flow", theme_name)


def mwis(theme, theme_name):
    """Graph with maximum weighted independent set solved using optimods."""
    fig, ax = create_figure(theme)

    # Create a clean planar graph where all nodes form clear angles
    # Using a grid-based structure with diagonal connections
    G = nx.Graph()

    # Add nodes with random weights
    np.random.seed(42)
    num_nodes = 12
    weights = np.random.uniform(0.5, 2.0, num_nodes)
    G.add_nodes_from(range(num_nodes))

    # Create edges - a 3x4 grid with some diagonals for interesting angles
    # Layout:  0---1---2---3
    #          |\ /|\ /|\ /|
    #          | X | X | X |
    #          |/ \|/ \|/ \|
    #          4---5---6---7
    #              |\ /|
    #              | X |
    #              |/ \|
    #          8---9--10--11
    edges = [
        # Top row horizontal
        (0, 1),
        (1, 2),
        (2, 3),
        # Middle row horizontal
        (4, 5),
        (5, 6),
        (6, 7),
        # Bottom row horizontal
        (8, 9),
        (9, 10),
        (10, 11),
        # Vertical connections
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
        (5, 9),
        (6, 10),
        # Diagonal connections for angles
        (1, 4),
        (2, 5),
        (1, 6),
        (2, 7),
        (5, 10),
        (6, 9),
    ]
    G.add_edges_from(edges)

    # Verify the graph is planar
    assert nx.is_planar(G), "Graph should be planar"

    # Solve MWIS using the actual optimod
    result_mwis = maximum_weighted_independent_set(G, weights)
    independent_set = set(result_mwis.x)

    # Solve max clique using the actual optimod
    result_clique = maximum_weighted_clique(G, weights)
    clique_set = set(result_clique.x)

    # Find nodes in both sets
    both_sets = independent_set & clique_set

    # Use manual grid layout for perfect alignment
    pos = {
        0: [0, 2],
        1: [1, 2],
        2: [2, 2],
        3: [3, 2],
        4: [0, 1],
        5: [1, 1],
        6: [2, 1],
        7: [3, 1],
        8: [0, 0],
        9: [1, 0],
        10: [2, 0],
        11: [3, 0],
    }

    # Scale positions to fit and center in canvas (0-10 range)
    for node in pos:
        x, y = pos[node]
        # Scale from 0-3 grid to 1.5-8.5 canvas range
        pos[node] = [1.5 + x * 7.0 / 3.0, 1.5 + y * 7.0 / 2.0]

    # Draw all edges
    for i, j in G.edges():
        ax.plot(
            [pos[i][0], pos[j][0]],
            [pos[i][1], pos[j][1]],
            color=theme["fg"],
            alpha=0.3,
            linewidth=2,
            zorder=1,
        )

    # Draw all nodes with uniform size
    node_size = 250
    for i in range(num_nodes):
        if i in both_sets:
            # Nodes in both sets - purple
            ax.scatter(
                pos[i][0],
                pos[i][1],
                s=node_size,
                color=theme["accent3"],  # purple
                edgecolor=theme["fg"],
                linewidth=1.5,
                zorder=3,
            )
        elif i in independent_set:
            # Nodes only in independent set - blue
            ax.scatter(
                pos[i][0],
                pos[i][1],
                s=node_size,
                color=theme["accent1"],  # blue
                edgecolor=theme["fg"],
                linewidth=1.5,
                zorder=3,
            )
        elif i in clique_set:
            # Nodes only in clique - red
            ax.scatter(
                pos[i][0],
                pos[i][1],
                s=node_size,
                color=theme["accent4"],  # red
                edgecolor=theme["fg"],
                linewidth=1.5,
                zorder=3,
            )
        else:
            # Other nodes - dimmed
            ax.scatter(
                pos[i][0],
                pos[i][1],
                s=node_size,
                color=theme["bg"] if theme["bg"] != "none" else theme["fg"],
                edgecolor=theme["fg"],
                linewidth=1.5,
                zorder=2,
                alpha=0.4,
            )

    save_figure(fig, "mwis", theme_name)


def opf(theme, theme_name):
    """Optimal power flow network."""
    fig, ax = create_figure(theme)

    # Bus locations
    buses = np.array([[2, 5], [4, 7], [4, 3], [6, 8], [6, 5], [6, 2], [8, 7], [8, 3]])

    # Transmission lines
    lines = [
        (0, 1),
        (0, 2),
        (1, 3),
        (1, 4),
        (2, 4),
        (2, 5),
        (3, 6),
        (4, 6),
        (4, 7),
        (5, 7),
    ]

    # Draw transmission lines
    for i, j in lines:
        ax.plot(
            [buses[i, 0], buses[j, 0]],
            [buses[i, 1], buses[j, 1]],
            color=theme["fg"],
            alpha=0.4,
            linewidth=theme["line_width"],
            zorder=1,
        )

    # Generators (with lightning symbol)
    generators = [0, 3, 7]
    for i in generators:
        # Draw circle for generator
        circle = plt.Circle(
            (buses[i, 0], buses[i, 1]),
            0.4,
            color=theme["accent1"],
            edgecolor=theme["fg"],
            linewidth=2,
            zorder=3,
        )
        ax.add_patch(circle)
        # Simple lightning bolt
        bolt_x = [buses[i, 0] - 0.1, buses[i, 0], buses[i, 0] + 0.1, buses[i, 0] - 0.05]
        bolt_y = [buses[i, 1] + 0.2, buses[i, 1], buses[i, 1] - 0.2, buses[i, 1] - 0.05]
        ax.plot(bolt_x, bolt_y, color=theme["bg"], linewidth=2, zorder=4)

    # Regular buses
    for i in range(len(buses)):
        if i not in generators:
            ax.scatter(
                buses[i, 0],
                buses[i, 1],
                s=200,
                color=theme["accent2"],
                edgecolor=theme["fg"],
                linewidth=2,
                zorder=2,
            )

    save_figure(fig, "opf", theme_name)


def portfolio(theme, theme_name):
    """Efficient frontier curve."""
    fig, ax = create_figure(theme)

    # Generate efficient frontier curve
    risk = np.linspace(1, 9, 100)
    ret = 2 + 4 * np.sqrt(risk - 1) - 0.15 * risk

    # Plot frontier
    ax.plot(
        risk, ret, color=theme["accent1"], linewidth=theme["line_width"] + 1, zorder=2
    )

    # Optimal portfolio point
    opt_idx = 45
    ax.scatter(
        risk[opt_idx],
        ret[opt_idx],
        s=300,
        color=theme["accent4"],
        edgecolor=theme["fg"],
        linewidth=2.5,
        zorder=3,
        marker="*",
    )

    # Feasible region (below frontier)
    ax.fill_between(risk, 0, ret, alpha=0.15, color=theme["accent1"], zorder=1)

    # Axes labels region
    ax.text(
        5, 0.8, "Risk →", ha="center", fontsize=11, color=theme["fg"], style="italic"
    )
    ax.text(
        0.8,
        5,
        "Return ↑",
        ha="center",
        fontsize=11,
        color=theme["fg"],
        style="italic",
        rotation=90,
    )

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    save_figure(fig, "portfolio", theme_name)


def qubo(theme, theme_name):
    """QUBO with spin states (up/down arrows)."""
    fig, ax = create_figure(theme)

    # Grid of spins
    np.random.seed(42)
    grid_size = 5
    spins = np.random.choice([-1, 1], size=(grid_size, grid_size))

    for i in range(grid_size):
        for j in range(grid_size):
            x = 2 + i * 1.6
            y = 2 + j * 1.6

            if spins[i, j] == 1:  # Up spin
                color = theme["accent1"]
                arrow = "↑"
            else:  # Down spin
                color = theme["accent3"]
                arrow = "↓"

            # Draw circle background
            circle = plt.Circle((x, y), 0.5, color=color, alpha=0.3, zorder=1)
            ax.add_patch(circle)

            # Draw arrow
            ax.text(
                x,
                y,
                arrow,
                ha="center",
                va="center",
                fontsize=24,
                fontweight="bold",
                color=color,
                zorder=2,
            )

    save_figure(fig, "qubo", theme_name)


def sharpe_ratio(theme, theme_name):
    """Sharpe ratio with tangency line."""
    fig, ax = create_figure(theme)

    # Efficient frontier
    risk = np.linspace(1, 9, 100)
    ret = 2 + 4 * np.sqrt(risk - 1) - 0.15 * risk
    ax.plot(
        risk,
        ret,
        color=theme["accent1"],
        linewidth=theme["line_width"],
        zorder=2,
        alpha=0.6,
    )

    # Risk-free rate
    rf = 2.5
    ax.axhline(
        y=rf, color=theme["fg"], linestyle="--", linewidth=1.5, alpha=0.4, zorder=1
    )

    # Tangency point (maximum Sharpe ratio)
    tang_idx = 40
    tang_risk = risk[tang_idx]
    tang_ret = ret[tang_idx]

    # Tangency line (Capital Market Line)
    cml_x = np.array([0, 9])
    slope = (tang_ret - rf) / tang_risk
    cml_y = rf + slope * cml_x
    ax.plot(
        cml_x,
        cml_y,
        color=theme["accent2"],
        linewidth=theme["line_width"] + 1,
        zorder=3,
        linestyle="-",
    )

    # Tangency point
    ax.scatter(
        tang_risk,
        tang_ret,
        s=350,
        color=theme["accent4"],
        edgecolor=theme["fg"],
        linewidth=2.5,
        zorder=4,
        marker="*",
    )

    # Labels
    ax.text(
        5, 0.8, "Risk →", ha="center", fontsize=11, color=theme["fg"], style="italic"
    )
    ax.text(
        0.8,
        5,
        "Return ↑",
        ha="center",
        fontsize=11,
        color=theme["fg"],
        style="italic",
        rotation=90,
    )

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    save_figure(fig, "sharpe-ratio", theme_name)


def workforce(theme, theme_name):
    """Workforce scheduling grid."""
    fig, ax = create_figure(theme)

    # Schedule grid
    workers = 5
    shifts = 7

    # Generate schedule
    np.random.seed(42)
    schedule = np.random.choice([0, 1], size=(workers, shifts), p=[0.35, 0.65])

    # Draw grid
    for i in range(workers):
        for j in range(shifts):
            x = 1.5 + j * 1.2
            y = 1.5 + i * 1.6

            if schedule[i, j] == 1:
                # Assigned shift
                rect = mpatches.Rectangle(
                    (x - 0.4, y - 0.5),
                    0.8,
                    1,
                    facecolor=theme["accent1"],
                    edgecolor=theme["fg"],
                    linewidth=1.5,
                    alpha=0.7,
                )
                ax.add_patch(rect)
                ax.text(
                    x,
                    y,
                    "✓",
                    ha="center",
                    va="center",
                    fontsize=14,
                    fontweight="bold",
                    color=theme["bg"],
                    zorder=3,
                )
            else:
                # Unassigned
                rect = mpatches.Rectangle(
                    (x - 0.4, y - 0.5),
                    0.8,
                    1,
                    facecolor=theme["bg"],
                    edgecolor=theme["fg"],
                    linewidth=1,
                    alpha=0.3,
                )
                ax.add_patch(rect)

    # Labels
    ax.text(
        5, 0.5, "Shifts →", ha="center", fontsize=10, color=theme["fg"], style="italic"
    )
    ax.text(
        0.5,
        5,
        "Workers",
        ha="center",
        fontsize=10,
        color=theme["fg"],
        style="italic",
        rotation=90,
    )

    save_figure(fig, "workforce", theme_name)


# Generate all icons
def main():
    icons = [
        ("Bipartite Matching", bipartite_matching),
        ("LAD Regression", lad_regression),
        ("Line Optimization", line_optimization),
        ("Max Flow/Min Cut", max_flow_min_cut),
        ("Metro Map", metromap),
        ("Min-Cost Flow", min_cost_flow),
        ("MWIS", mwis),
        ("Optimal Power Flow", opf),
        ("Portfolio", portfolio),
        ("QUBO", qubo),
        ("Sharpe Ratio", sharpe_ratio),
        ("Workforce", workforce),
    ]

    print("Generating OptiMods icons...")
    print(f"Output directory: {ICON_DIR}\n")

    for name, func in icons:
        print(f"Generating {name}...")
        func(LIGHT_THEME, "light")
        func(DARK_THEME, "dark")
        print()

    print(f"✓ All icons generated successfully!")
    print(f"✓ Total: {len(icons) * 2} icons created")


if __name__ == "__main__":
    main()
