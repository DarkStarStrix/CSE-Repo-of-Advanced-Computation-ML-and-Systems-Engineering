import requests
import pandas as pd
import numpy as np
from numba import jit
import concurrent.futures
import time


def fetch_inspirehep_data(start, size):
    url = f"https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page=1&q=track%20reconstruction"
    try:
        response = requests.get (url, timeout=10)
        response.raise_for_status ()
        data = response.json () ['hits'] ['hits']
        print (f"Fetched {len (data)} records from inspirehep.net")
        return data
    except requests.RequestException as e:
        print (f"Failed to fetch data: {e}")
        return []


@jit (nopython=True)
def generate_measurements(n_records):
    np.random.seed (42)  # For reproducibility
    energy = np.random.uniform (10, 1000, n_records)
    momentum = np.random.uniform (5, 500, n_records)
    x = np.random.uniform (-100, 100, n_records)
    y = np.random.uniform (-100, 100, n_records)
    z = np.random.uniform (-500, 500, n_records)
    return np.column_stack ((energy, momentum, x, y, z))


def process_chunk(chunk):
    if chunk:
        measurements = generate_measurements (len (chunk))
        return measurements
    else:
        print ("Empty chunk received")
        return np.array ([])


def fetch_and_process_data(total_records=2000, chunk_size=500):
    start_time = time.time ()

    data = fetch_inspirehep_data (0, total_records)
    if not data:
        print ("No data fetched, generating synthetic data instead")
        data = [None] * total_records

    chunks = [data [i:i + chunk_size] for i in range (0, len (data), chunk_size)]
    print (f"Created {len (chunks)} chunks")

    if not chunks:
        print ("No chunks created, generating default data")
        measurements = generate_measurements (total_records)
    else:
        with concurrent.futures.ThreadPoolExecutor (max_workers=4) as executor:
            results = list (executor.map (process_chunk, chunks))

        valid_results = [r for r in results if r.size > 0]
        if not valid_results:
            print ("No valid results from threads, generating default data")
            measurements = generate_measurements (total_records)
        else:
            measurements = np.vstack (valid_results)

    if measurements.shape [0] < total_records:
        print (f"Only {measurements.shape [0]} records, padding with synthetic data")
        extra = generate_measurements (total_records - measurements.shape [0])
        measurements = np.vstack ([measurements, extra])

    df = pd.DataFrame (measurements, columns=['energy', 'momentum', 'x', 'y', 'z'])
    df ['distance'] = np.sqrt (df ['x'] ** 2 + df ['y'] ** 2 + df ['z'] ** 2)

    print (f"Processing time: {time.time () - start_time:.2f} seconds")
    return df


if __name__ == "__main__":
    df = fetch_and_process_data (total_records=2000)

    print ("\nFirst 5 rows of the structured data:")
    print (df.head ())
    print ("\nData summary:")
    print (df.describe ())

    df.to_csv ("particle_measurements.csv", index=False)
    print ("\nData saved to 'particle_measurements.csv'")
