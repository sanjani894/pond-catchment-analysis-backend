from fastapi import FastAPI

app = FastAPI(title="Pond Catchment Analysis Backend")


@app.get("/")
def root():
    return {"message": "Pond Catchment Analysis Backend is running"}


@app.post("/analyzeContour")
def analyze_contour():
    return {
        "message": "Contour analysis endpoint is ready"
    }