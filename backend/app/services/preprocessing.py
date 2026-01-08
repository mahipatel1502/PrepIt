import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_data(df: pd.DataFrame):

    report = []

    # Remove duplicates
    initial_rows = df.shape[0]
    df = df.drop_duplicates()
    report.append(f"Removed {initial_rows - df.shape[0]} duplicate rows")

    # Handle missing values
    for col in df.columns:
        if df[col].dtype == "object":
            df[col].fillna(df[col].mode()[0], inplace=True)
        else:
            df[col].fillna(df[col].mean(), inplace=True)

    report.append("Handled missing values")

    # Encode categorical columns
    encoder = LabelEncoder()
    for col in df.select_dtypes(include="object"):
        df[col] = encoder.fit_transform(df[col])

    report.append("Encoded categorical columns")

    # Scale numerical features
    scaler = StandardScaler()
    df[df.columns] = scaler.fit_transform(df)

    report.append("Applied feature scaling")

    return df, report
