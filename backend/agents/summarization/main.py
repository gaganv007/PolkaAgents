from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "summarization Agent Ready"}

@app.post("/predict")
def predict():
    return {"result": "Sample prediction from summarization agent"}
