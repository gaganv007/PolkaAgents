from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "job_application Agent Ready"}

@app.post("/predict")
def predict():
    return {"result": "Sample prediction from job_application agent"}
