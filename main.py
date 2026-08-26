from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Pond Catchment Analysis Backend")


@app.get("/")
def root():
    return {"message": "Pond Catchment Analysis Backend is running"}


@app.post("/analyzeContour")
async def analyze_contour(file: UploadFile = File(...)):
    return {
        "message": "Contour file received successfully",
        "filename": file.filename
    }
