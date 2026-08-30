import numpy as np

from fastapi import FastAPI, UploadFile, File, HTTPException

from kml_parser import parse_contours
from terrain_builder import build_dem
from flow_analysis import (
    calculate_flow_direction,
    calculate_flow_accumulation
)


app = FastAPI(title="Pond Catchment Analysis Backend")


@app.get("/")
def root():
    return {
        "message": "Pond Catchment Analysis Backend is running"
    }


@app.post("/analyzeContour")
async def analyze_contour(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        result = parse_contours(
            file_bytes=file_bytes,
            filename=file.filename or ""
        )

        terrain = build_dem(
            contours=result["contours"],
            bounds=result["bounds"]
        )

        flow_direction = calculate_flow_direction(
            elevation_grid=terrain["elevation_grid"],
            cell_width_m=terrain["cell_width_m"],
            cell_height_m=terrain["cell_height_m"]
        )

        flow_accumulation = calculate_flow_accumulation(
            flow_direction
        )

        response = {
            key: value
            for key, value in result.items()
            if key != "contours"
        }

        response["terrain"] = {
            "grid_size": terrain["grid_size"],
            "cell_width_m": terrain["cell_width_m"],
            "cell_height_m": terrain["cell_height_m"],
            "min_elevation": terrain["min_elevation"],
            "max_elevation": terrain["max_elevation"]
        }

        response["flow_direction"] = {
            "grid_rows": int(flow_direction.shape[0]),
            "grid_columns": int(flow_direction.shape[1])
        }

        response["flow_accumulation"] = {
            "max_accumulation": float(
                np.max(flow_accumulation)
            ),
            "mean_accumulation": float(
                np.mean(flow_accumulation)
            )
        }

        return response

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )