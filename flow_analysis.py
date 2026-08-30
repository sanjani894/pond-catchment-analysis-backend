import numpy as np


# D8 neighbor directions.
# Each tuple contains:
# (row_change, column_change)
DIRECTIONS = [
    (-1, 0),   # North
    (-1, 1),   # North-East
    (0, 1),    # East
    (1, 1),    # South-East
    (1, 0),    # South
    (1, -1),   # South-West
    (0, -1),   # West
    (-1, -1)   # North-West
]


def calculate_flow_direction(elevation_grid, cell_width_m, cell_height_m):
    """
    Calculate the D8 flow direction for an elevation grid.

    Each cell flows toward the neighboring cell with the
    steepest downward slope.

    Returns:
        A grid containing the direction index for each cell.
        -1 means no lower neighboring cell was found.
    """

    rows, columns = elevation_grid.shape

    flow_direction = np.full(
        (rows, columns),
        -1,
        dtype=int
    )

    for row in range(rows):
        for column in range(columns):

            current_elevation = elevation_grid[row, column]

            if np.isnan(current_elevation):
                continue

            best_direction = -1
            best_slope = 0.0

            for direction_index, (dr, dc) in enumerate(DIRECTIONS):

                neighbor_row = row + dr
                neighbor_column = column + dc

                # Skip neighbors outside the grid.
                if (
                    neighbor_row < 0
                    or neighbor_row >= rows
                    or neighbor_column < 0
                    or neighbor_column >= columns
                ):
                    continue

                neighbor_elevation = elevation_grid[
                    neighbor_row,
                    neighbor_column
                ]

                if np.isnan(neighbor_elevation):
                    continue

                elevation_drop = (
                    current_elevation - neighbor_elevation
                )

                if elevation_drop <= 0:
                    continue

                # Calculate horizontal distance.
                if dr != 0 and dc != 0:
                    distance = np.sqrt(
                        cell_width_m ** 2
                        + cell_height_m ** 2
                    )
                elif dc != 0:
                    distance = cell_width_m
                else:
                    distance = cell_height_m

                slope = elevation_drop / distance

                if slope > best_slope:
                    best_slope = slope
                    best_direction = direction_index

            flow_direction[row, column] = best_direction

    return flow_direction