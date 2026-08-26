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

        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))