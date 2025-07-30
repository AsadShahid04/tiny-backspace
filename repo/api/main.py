from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import code

app = FastAPI()

class TrainRequest(BaseModel):
    input_file: str
    model_name: str
    experiment_name: str

    @validator('input_file')
    def validate_input_file(cls, v):
        if not v.endswith('.csv'):
            raise ValueError('Input file must be a CSV file')
        return v

    @validator('model_name')
    def validate_model_name(cls, v):
        allowed_models = ['random_forest', 'xgboost']
        if v not in allowed_models:
            raise ValueError(f'Model name must be one of: {allowed_models}')
        return v

    @validator('experiment_name')
    def validate_experiment_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Experiment name cannot be empty')
        return v

class PredictRequest(BaseModel):
    model_name: str
    input_data: dict

    @validator('model_name')
    def validate_model_name(cls, v):
        allowed_models = ['random_forest', 'xgboost']
        if v not in allowed_models:
            raise ValueError(f'Model name must be one of: {allowed_models}')
        return v

    @validator('input_data')
    def validate_input_data(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Input data cannot be empty')
        required_fields = ['feature1', 'feature2']  # Add your required features
        missing_fields = [field for field in required_fields if field not in v]
        if missing_fields:
            raise ValueError(f'Missing required fields: {missing_fields}')
        return v

@app.post("/train")
async def train_model(request: TrainRequest):
    try:
        result = code.train_model(
            request.input_file,
            request.model_name,
            request.experiment_name
        )
        return {"message": "Training completed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        result = code.predict(
            request.model_name,
            request.input_data
        )
        return {"predictions": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}