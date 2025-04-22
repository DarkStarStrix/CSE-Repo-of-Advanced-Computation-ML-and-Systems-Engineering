import pandas as pd
import numpy as np
from mp_api.client import MPRester
from concurrent.futures import ThreadPoolExecutor
from numba import jit
from tqdm import tqdm
import warnings

warnings.filterwarnings ('ignore')

API_KEY = "aoV2C7VXpxARAsNuvL061mvKGzAOXH5L"

# Define column structure
COLUMNS = {
    'material_properties': [
        "formula_pretty",
        "material_id",
        "formation_energy_per_atom",
        "band_gap",
        "density",
        "volume",
        "symmetry.symbol",
        "energy_per_atom"
    ],
    'composition': [
        "elements",
        "n_elements",
        "contains_transition_metal"
    ],
    'electronic': [
        "band_gap",
        "is_semiconductor"
    ],
    'mechanical': [
        "density",
        "volume"
    ]
}


@jit (nopython=True)
def process_numerical_features(data_array):
    """JIT-compiled numerical feature processing"""
    # Replace NaN with mean of column
    for col in range (data_array.shape [1]):
        mask = np.isnan (data_array [:, col])
        col_mean = np.nanmean (data_array [:, col])
        data_array [mask, col] = col_mean

    # Standardize features
    for col in range (data_array.shape [1]):
        mean = np.mean (data_array [:, col])
        std = np.std (data_array [:, col])
        if std != 0:
            data_array [:, col] = (data_array [:, col] - mean) / std

    return data_array


def fetch_material_batch(batch):
    """Process a batch of materials"""
    fields = [
        "formula_pretty",
        "material_id",
        "formation_energy_per_atom",
        "band_gap",
        "density",
        "volume",
        "energy_per_atom",
        "elements"
    ]

    with MPRester(API_KEY) as mpr:
        results = mpr.materials.summary.search(
            elements=["Li"],
            num_elements=(2, None),
            fields=fields,
            chunk_size=batch
        )
        return [doc.dict() for doc in results]


def process_dataframe(df):
    """Process and structure the dataframe"""
    # First check available columns
    available_columns = df.columns.tolist()
    print("Available columns:", available_columns)

    # Process numerical features
    numerical_cols = [col for col in [
        'formation_energy_per_atom', 'band_gap', 'density',
        'volume', 'energy_per_atom'
    ] if col in available_columns]

    if numerical_cols:
        numerical_data = df[numerical_cols].values.astype(np.float64)
        processed_data = process_numerical_features(numerical_data)
        df[numerical_cols] = processed_data

    # Add derived features with None handling
    if 'elements' in available_columns:
        df['n_elements'] = df['elements'].apply(lambda x: len(x) if x is not None else 0)
        df['contains_transition_metal'] = df['elements'].apply(
            lambda x: any(e in x for e in ['Fe', 'Co', 'Ni', 'Mn']) if x is not None else False
        )

    if 'band_gap' in available_columns:
        df['is_semiconductor'] = df['band_gap'].apply(
            lambda x: True if isinstance(x, (int, float)) and 0 < x < 4.0 else False
        )

    # Drop rows with missing essential data
    df = df.dropna(subset=['material_id', 'formula_pretty'])

    # Structure columns based on available data
    final_columns = [col for col in [
        'material_id',
        'formula_pretty',
        'n_elements',
        'contains_transition_metal',
        'formation_energy_per_atom',
        'energy_per_atom',
        'band_gap',
        'is_semiconductor',
        'density',
        'volume',
        'elements'
    ] if col in df.columns]

    return df[final_columns]


def main():
    # Parallel data fetching
    batch_sizes = [100, 100, 100, 100]
    with ThreadPoolExecutor (max_workers=4) as executor:
        futures = [executor.submit (fetch_material_batch, batch) for batch in batch_sizes]
        data = []
        for future in tqdm (futures, desc="Fetching data"):
            data.extend (future.result ())

    # Create and process DataFrame
    df = pd.DataFrame (data)
    df = process_dataframe (df)

    # Save structured CSV
    csv_filename = "lithium_battery_materials.csv"
    df.to_csv (csv_filename, index=False)

    # Print summary
    print ("\n✅ Dataset Summary:")
    print (f"Total materials: {len (df)}")
    print ("\nNumerical Features Statistics:")
    print (df.describe ().round (3))
    print ("\nCategorial Features Summary:")
    print (f"Semiconductor materials: {df ['is_semiconductor'].sum ()}")
    print (f"Materials with transition metals: {df ['contains_transition_metal'].sum ()}")
    print (f"\nData saved to: {csv_filename}")


if __name__ == "__main__":
    main ()
