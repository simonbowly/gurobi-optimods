#!/usr/bin/env python3
"""
Generate a dark mode facility location optimization icon.
Shows facilities (warehouses) connected to customer locations.
"""

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

# Set up the figure with high resolution
fig, ax = plt.subplots(1, 1, figsize=(64, 48), dpi=100)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")

# Set background color to transparent
fig.patch.set_facecolor("none")
ax.set_facecolor("none")

# Define colors for dark mode - lighter, more vibrant colors
facility_color = "#4DA6D6"  # Lighter blue for facilities
customer_color = "#E85D9A"  # Lighter pink/purple for customers
connection_color = "#FFB347"  # Lighter orange for connections

# Define facility locations (warehouses)
facilities = [(25, 70), (75, 70), (50, 30)]

# Define customer locations (more scattered)
customers = [
    (15, 80),
    (35, 85),
    (30, 60),
    (20, 50),
    (65, 85),
    (85, 80),
    (80, 60),
    (70, 55),
    (30, 40),
    (40, 25),
    (55, 20),
    (70, 25),
    (45, 50),
    (55, 55),
    (50, 75),
]

# Draw connections from customers to nearest facility
for customer in customers:
    # Find nearest facility
    min_dist = float("inf")
    nearest_facility = None
    for facility in facilities:
        dist = np.sqrt(
            (customer[0] - facility[0]) ** 2 + (customer[1] - facility[1]) ** 2
        )
        if dist < min_dist:
            min_dist = dist
            nearest_facility = facility

    # Draw connection line
    ax.plot(
        [customer[0], nearest_facility[0]],
        [customer[1], nearest_facility[1]],
        color=connection_color,
        alpha=0.5,
        linewidth=2.5,
        zorder=1,
    )

# Draw facilities (large buildings/warehouses)
for facility in facilities:
    # Shadow (lighter for dark mode)
    shadow = Rectangle(
        (facility[0] - 4.3, facility[1] - 4.3),
        8,
        8,
        facecolor="black",
        alpha=0.4,
        zorder=2,
    )
    ax.add_patch(shadow)

    # Main building
    building = Rectangle(
        (facility[0] - 4, facility[1] - 4),
        8,
        8,
        facecolor=facility_color,
        edgecolor="#2C2C2C",
        linewidth=3,
        zorder=3,
    )
    ax.add_patch(building)

    # Roof detail
    roof_points = np.array(
        [
            [facility[0] - 4.5, facility[1] + 4],
            [facility[0], facility[1] + 5.5],
            [facility[0] + 4.5, facility[1] + 4],
        ]
    )
    roof = plt.Polygon(
        roof_points,
        facecolor=facility_color,
        edgecolor="#2C2C2C",
        linewidth=3,
        zorder=3,
    )
    ax.add_patch(roof)

    # Door (darker for contrast)
    door = Rectangle(
        (facility[0] - 1, facility[1] - 4),
        2,
        3,
        facecolor="#2C2C2C",
        alpha=0.8,
        zorder=4,
    )
    ax.add_patch(door)

# Draw customers (location pins)
for customer in customers:
    # Shadow
    shadow_circle = Circle(
        (customer[0] + 0.3, customer[1] - 0.3),
        2.2,
        facecolor="black",
        alpha=0.4,
        zorder=5,
    )
    ax.add_patch(shadow_circle)

    # Pin circle
    pin_circle = Circle(
        customer,
        2,
        facecolor=customer_color,
        edgecolor="#2C2C2C",
        linewidth=2.5,
        zorder=6,
    )
    ax.add_patch(pin_circle)

    # Pin center dot (darker for contrast)
    center_dot = Circle(customer, 0.7, facecolor="#2C2C2C", zorder=7)
    ax.add_patch(center_dot)

# Add title text at bottom (light color for dark mode)
title_text = "FACILITY LOCATION"
ax.text(
    50,
    8,
    title_text,
    fontsize=80,
    weight="bold",
    ha="center",
    va="center",
    color="#E0E0E0",
    family="sans-serif",
    zorder=10,
)

# Save the icon
plt.tight_layout(pad=0)
plt.savefig(
    "/workspace/docs/source/mods/icons/facility-location-dark.png",
    dpi=100,
    bbox_inches="tight",
    pad_inches=0.2,
    facecolor="none",
    transparent=True,
)
print(
    "Dark mode icon generated successfully at: /workspace/docs/source/mods/icons/facility-location-dark.png"
)
print(f"Image size: 6400x4800 pixels")

plt.close()
