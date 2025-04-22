import numpy as np
import qutip as qt
from itertools import product
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd


class QuantumTomographySimulator:
    def __init__(self, n_qubits=2):
        self.n_qubits = n_qubits
        self.dim = 2 ** n_qubits
        self.pauli_ops = self._generate_pauli_operators ()

    def _generate_pauli_operators(self):
        I = qt.qeye (2)
        X = qt.sigmax ()
        Y = qt.sigmay ()
        Z = qt.sigmaz ()

        paulis = {'I': I, 'X': X, 'Y': Y, 'Z': Z}

        ops = []
        for p in product (['I', 'X', 'Y', 'Z'], repeat=self.n_qubits):
            op = paulis [p [0]]
            for pauli in p [1:]:
                op = qt.tensor (op, paulis [pauli])
            ops.append ((p, op))

        return ops

    def prepare_test_state(self, state_type='ghz'):
        if state_type == 'ghz':
            basis_0 = qt.basis ([2] * self.n_qubits, [0] * self.n_qubits)
            basis_1 = qt.basis ([2] * self.n_qubits, [1] * self.n_qubits)
            state = (basis_0 + basis_1).unit ()
        elif state_type == 'w':
            state = qt.zero_ket (2 ** self.n_qubits)
            for i in range (self.n_qubits):
                basis = [0] * self.n_qubits
                basis [i] = 1
                state += qt.basis ([2] * self.n_qubits, basis)
            state = state.unit ()
        else:
            state = qt.rand_ket (2 ** self.n_qubits)

        return state

    def generate_sparse_measurements(self, state, sparsity=0.3, noise_level=0.01):
        rho = state * state.dag ()
        measurements = []
        operators = []
        indices = []

        for idx, (pauli_string, op) in enumerate (self.pauli_ops):
            expect = (op * rho).tr ().real
            noisy_expect = expect + np.random.normal (0, noise_level)
            if np.random.random () < sparsity:
                measurements.append (noisy_expect)
                operators.append (op)
                indices.append (idx)

        return np.array (measurements), operators, indices

    def reconstruct_state(self, measurements, operators):
        rho = qt.Qobj (np.eye (self.dim) / self.dim, dims=[[2] * self.n_qubits, [2] * self.n_qubits])

        def cost_function(params):
            rho_test = qt.Qobj (params.reshape (self.dim, self.dim), dims=[[2] * self.n_qubits, [2] * self.n_qubits])
            error = 0
            for measurement, op in zip (measurements, operators):
                expect = (op * rho_test).tr ().real
                error += (expect - measurement) ** 2
            return error

        from scipy.optimize import minimize
        result = minimize (cost_function, rho.full ().flatten (), method='BFGS', options={'maxiter': 1000})

        if result.success:
            return qt.Qobj (result.x.reshape (self.dim, self.dim), dims=[[2] * self.n_qubits, [2] * self.n_qubits])
        else:
            print ("Optimization failed:", result.message)
            return None

    @staticmethod
    def analyze_results(original_state, reconstructed_state):
        original_dm = original_state * original_state.dag ()

        results = {
            'fidelity': qt.fidelity (original_dm, reconstructed_state),
            'trace_distance': qt.tracedist (original_dm, reconstructed_state),
            'purity_original': (original_dm * original_dm).tr ().real,
            'purity_reconstructed': (reconstructed_state * reconstructed_state).tr ().real
        }

        return results

    @staticmethod
    def visualize_states(original_state, reconstructed_state, filename_prefix):
        fig = plt.figure (figsize=(12, 4))

        ax1 = fig.add_subplot (121, projection='3d')
        hist1, _ = qt.matrix_histogram (original_state * original_state.dag (), ax=ax1)
        ax1.set_title ('Original State')

        ax2 = fig.add_subplot (122, projection='3d')
        hist2, _ = qt.matrix_histogram (reconstructed_state, ax=ax2)
        ax2.set_title ('Reconstructed State')

        plt.subplots_adjust (left=0.05, right=0.95, top=0.9, bottom=0.1, wspace=0.3)

        hist1.set_label ('Original State')
        hist2.set_label ('Reconstructed State')

        ax1.legend (loc='upper left', bbox_to_anchor=(1, 1))
        ax2.legend (loc='upper left', bbox_to_anchor=(1, 1))

        plt.savefig (f"{filename_prefix}_states.png")
        plt.close (fig)


def generate_tomography_dataset(n_qubits=2, state_type='ghz', sparsity=0.3, noise_level=0.01, num_samples=100):
    data = []

    for _ in range (num_samples):
        simulator = QuantumTomographySimulator (n_qubits)
        original_state = simulator.prepare_test_state (state_type)
        measurements, operators, indices = simulator.generate_sparse_measurements (
            original_state,
            sparsity=sparsity,
            noise_level=noise_level
        )
        reconstructed_state = simulator.reconstruct_state (measurements, operators)
        results = simulator.analyze_results (original_state, reconstructed_state)
        data.append (results)

    df = pd.DataFrame (data)
    return df


def save_dataset_to_csv(df, filename):
    df.to_csv (filename, index=False)


dataset = generate_tomography_dataset (num_samples=500)
save_dataset_to_csv (dataset, 'quantum_tomography_dataset.csv')

print (dataset.head ())

print ("\nTomography Results:")
for key in dataset.columns:
    print (f"{key}: {dataset [key].mean ():.4f}")

fig, axes = plt.subplots (1, 2, figsize=(12, 4))
fig.suptitle ('Tomography Results')

axes [0].hist (dataset ['fidelity'], bins=20, color='skyblue', edgecolor='black')
axes [0].set_title ('Fidelity')
axes [0].set_xlabel ('Fidelity')
axes [0].set_ylabel ('Frequency')

axes [1].hist (dataset ['trace_distance'], bins=20, color='salmon', edgecolor='black')
axes [1].set_title ('Trace Distance')
axes [1].set_xlabel ('Trace Distance')
axes [1].set_ylabel ('Frequency')

plt.tight_layout ()
plt.savefig ('tomography_results.png')
plt.show ()


def main():
    n_qubits = 2
    simulator = QuantumTomographySimulator (n_qubits)
    original_state = simulator.prepare_test_state ('ghz')
    measurements, operators, indices = simulator.generate_sparse_measurements (
        original_state,
        sparsity=0.3,
        noise_level=0.01
    )
    reconstructed_state = simulator.reconstruct_state (measurements, operators)
    results = simulator.analyze_results (original_state, reconstructed_state)
    print ("\nTomography Results:")
    for key, value in results.items ():
        print (f"{key}: {value:.4f}")

    simulator.visualize_states (original_state, reconstructed_state, 'quantum_tomography')

    total_measurements = len (simulator.pauli_ops)
    actual_measurements = len (measurements)
    print (f"\nMeasurement sparsity: {actual_measurements}/{total_measurements} "
           f"({actual_measurements / total_measurements:.1%})")


if __name__ == "__main__":
    main ()
