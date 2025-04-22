import numpy as np
import pickle


def himmelblau(x, y):
    return (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2


def generate_dataset(filename='nonconvex_landscape.pkl', grid_size=50):
    x = np.linspace (-5, 5, grid_size)
    y = np.linspace (-5, 5, grid_size)
    X, Y = np.meshgrid (x, y)
    Z = himmelblau (X, Y)

    dataset = {
        'X': X,
        'Y': Y,
        'Z': Z
    }

    with open (filename, 'wb') as f:
        pickle.dump (dataset, f)
    print (f"Dataset saved to {filename}")


if __name__ == "__main__":
    generate_dataset ()
