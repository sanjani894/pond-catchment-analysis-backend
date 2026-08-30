import numpy as np


def normalize(values):
    """Normalize an array to the range 0 to 1."""

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:
        return np.zeros_like(values, dtype=float)

    return (values - minimum) / (maximum - minimum)


def select_pond_candidate(
    elevation_grid,
    flow_accumulation,
    x_grid,
    y_grid,
    transformer,
    accumulation_weight=0.7,
    elevation_weight=0.3
):
    """
    Select a terrain-derived pond candidate and return
    its geographic coordinates.
    """

    valid = (
        ~np.isnan(elevation_grid)
        & ~np.isnan(flow_accumulation)
    )

    if not np.any(valid):
        raise ValueError("No valid terrain cells available")

    accumulation_score = normalize(
        flow_accumulation
    )

    elevation_score = 1.0 - normalize(
        elevation_grid
    )

    suitability = (
        accumulation_weight * accumulation_score
        + elevation_weight * elevation_score
    )

    suitability[~valid] = -np.inf

    candidate_row, candidate_column = np.unravel_index(
        np.argmax(suitability),
        suitability.shape
    )

    x = x_grid[candidate_column]
    y = y_grid[candidate_row]

    longitude, latitude = transformer.transform(
        x,
        y,
        direction="INVERSE"
    )

    return {
        "row": int(candidate_row),
        "column": int(candidate_column),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "elevation": float(
            elevation_grid[
                candidate_row,
                candidate_column
            ]
        ),
        "flow_accumulation": float(
            flow_accumulation[
                candidate_row,
                candidate_column
            ]
        ),
        "suitability_score": float(
            suitability[
                candidate_row,
                candidate_column
            ]
        )
    }