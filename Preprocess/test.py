from auto_preprocessor import run_preprocessing

result = run_preprocessing('/Users/mahipatel/Documents/GitHub/PrepIt/Preprocess/StatewiseTestingDetails.csv')

print(f"✅ Done!")
print(f"Original shape: {result['report']['original_shape']}")
print(f"Final shape: {result['X'].shape}")
print(f"Features: {result['feature_names']}")
print(f"Dropped: {result['report']['dropped_columns']}")

import pandas as pd
import numpy as np

# After getting the result, save to CSV:
cleaned_df = pd.DataFrame(result['X'], columns=result['feature_names'])
cleaned_df.to_csv('processed/cleaned_data.csv', index=False)
print(f"\n💾 Saved to: processed/cleaned_data.csv")