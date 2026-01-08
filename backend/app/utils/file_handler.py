from fastapi import HTTPException

ALLOWED_EXTENSIONS = ["csv", "xlsx"]

def validate_file(filename: str):
    ext = filename.split(".")[-1]

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are allowed"
        )
