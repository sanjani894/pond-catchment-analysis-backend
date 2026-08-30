from terrain_builder import build_dem
from fastapi import FastAPI, UploadFile, File, HTTPException

from kml_parser import parse_contours


app = FastAPI(title="Pond Catchment Analysis Backend")


@app.get("/")
def root():
    return {"message": "Pond Catchment Analysis Backend is running"}


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

        return response

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))