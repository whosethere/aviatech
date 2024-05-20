from fastapi import FastAPI, File, UploadFile
import pandas as pd
import numpy as np
import uvicorn

app = FastAPI()

def detect_landing_takeoff_with_details(data, altitude_drop_threshold, speed_drop_threshold, seq_length):
    landing_details = []
    takeoff_details = []
    in_landing_sequence = False
    
    for i in range(len(data) - seq_length):
        altitudes = data.iloc[i:i + seq_length]['Altitude'].values
        speeds = data.iloc[i:i + seq_length]['Speed'].values
        directions = data.iloc[i:i + seq_length]['Direction'].values
        
        altitude_drop = altitudes[0] - altitudes[-1]
        speed_drop = speeds[0] - speeds[-1]
        direction_variation = max(directions) - min(directions)
        
        
        if altitude_drop > altitude_drop_threshold and speed_drop > speed_drop_threshold and direction_variation < direction_variation_threshold:
            if not in_landing_sequence:
                in_landing_sequence = True
                landing_details.append({
                    'Timestamp': int(data.iloc[i + seq_length - 1]['Timestamp']),
                    'Position': data.iloc[i + seq_length - 1]['Position'],
                    'Row Number': int(data.iloc[i + seq_length - 1].name)
                })
        else:
            if in_landing_sequence:
                in_landing_sequence = False
                takeoff_details.append({
                    'Timestamp': int(data.iloc[i + seq_length - 1]['Timestamp']),
                    'Position': data.iloc[i + seq_length - 1]['Position'],
                    'Row Number': int(data.iloc[i + seq_length - 1].name)
                })
                         
    return landing_details, takeoff_details


@app.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    df = pd.read_csv(file.file)
    landing_details, takeoff_details = detect_landing_takeoff_with_details(df, 50, 10, 5)
    return {"takeoff_details": takeoff_details}

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
