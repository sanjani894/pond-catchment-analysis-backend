import numpy as np

from fastapi import FastAPI, UploadFile, File, HTTPException

from kml_parser import parse_contours
from terrain_builder import build_dem
from flow_analysis import (
    calculate_flow_direction,
    calculate_flow_accumulation,
    delineate_catchment
)
from pond_selection import select_pond_candidate


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

        # 1. Parse contour map
        result = parse_contours(
            file_bytes=file_bytes,
            filename=file.filename or ""
        )

        # 2. Build elevation grid / DEM
        terrain = build_dem(
            contours=result["contours"],
            bounds=result["bounds"]
        )

        # 3. Calculate flow direction
        flow_direction = calculate_flow_direction(
            elevation_grid=terrain["elevation_grid"],
            cell_width_m=terrain["cell_width_m"],
            cell_height_m=terrain["cell_height_m"]
        )

        # 4. Calculate flow accumulation
        flow_accumulation = calculate_flow_accumulation(
            flow_direction
        )

        # 5. Select pond candidate
        pond_candidate = select_pond_candidate(
            elevation_grid=terrain["elevation_grid"],
            flow_accumulation=flow_accumulation,
            x_grid=terrain["x_grid"],
            y_grid=terrain["y_grid"],
            transformer=terrain["transformer"]
        )

        # 6. Delineate catchment for selected pond
        catchment = delineate_catchment(
            flow_direction=flow_direction,
            outlet_row=pond_candidate["row"],
            outlet_column=pond_candidate["column"],
            cell_width_m=terrain["cell_width_m"],
            cell_height_m=terrain["cell_height_m"]
)
        
        # 8. Create API response
        response = {
            key: value
            for key, value in result.items()
            if key != "contours"
        }

        # 9. Add terrain information
        response["terrain"] = {
            "grid_size": terrain["grid_size"],
            "cell_width_m": terrain["cell_width_m"],
            "cell_height_m": terrain["cell_height_m"],
            "min_elevation": terrain["min_elevation"],
            "max_elevation": terrain["max_elevation"]
        }

        # 10. Add flow direction information
        response["flow_direction"] = {
            "grid_rows": int(flow_direction.shape[0]),
            "grid_columns": int(flow_direction.shape[1])
        }

        # 11. Add flow accumulation information
        response["flow_accumulation"] = {
            "max_accumulation": float(
                np.max(flow_accumulation)
            ),
            "mean_accumulation": float(
                np.mean(flow_accumulation)
            )
        }

        # 12. Add pond candidate
        response["pond_candidate"] = pond_candidate

        # 13. Add catchment information
        response["catchment"] = {
           "cell_count": catchment["cell_count"],
           "cell_area_m2": catchment["cell_area_m2"],
           "area_m2": catchment["area_m2"],
           "area_hectares": catchment["area_hectares"]
}

        return response

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )