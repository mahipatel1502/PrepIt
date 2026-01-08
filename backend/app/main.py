from fastapi import FastAPI, UploadFile, File
import pandas as pd

app = FastAPI()

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read Excel file
        df = pd.read_excel(file.file)

        # Example: print first rows
        print(df.head())

        return {
            "message": "File uploaded successfully",
            "rows": len(df),
            "columns": list(df.columns)
        }

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}
