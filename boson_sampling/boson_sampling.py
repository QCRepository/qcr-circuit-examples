"""
Example of the boson sampling scheme proposed by Aaronson and Arkhipov using Piquasso.

For more details on boson sampling, see:
- [BosonSampling](https://en.wikipedia.org/wiki/Boson_sampling)
- [Original Paper](https://arxiv.org/abs/1011.3245)
- [Piquasso Documentation](https://piquasso.readthedocs.io/en/latest/tutorials/boson-sampling.html)
"""

import piquasso as pq
from scipy.stats import unitary_group

def boson_sampling_program(input_state_vector, interferometer_matrix):
    """Construct a boson sampling quantum program using a given input state and interferometer matrix.

    Args:
        input_state_vector (list): The initial occupation number state vector for the boson sampling circuit
        interferometer_matrix (ndarray): Unitary matrix representing the interferometer transformation

    Returns:
        pq.Program: A Piquasso quantum program for boson sampling
    """
    with pq.Program() as program:
        pq.Q(all) | pq.StateVector(input_state_vector)
        pq.Q(all) | pq.Interferometer(interferometer_matrix)
        pq.Q(all) | pq.ParticleNumberMeasurement()
    return program

if __name__ == "__main__":
    # Example parameters
    num_modes = 7
    num_shots = 100

    # Take a specific input state for the boson sampling example
    # Here, we use a state with 3 photons in the first three modes
    # and vacuum in the rest
    input_state_vector = [1, 1, 1, 0, 0, 0, 0]
    total_photons = sum(input_state_vector)

    # Generate a random example matrix for the interferometer from the unitary group
    interferometer_matrix = unitary_group.rvs(num_modes)

    program = boson_sampling_program(input_state_vector, interferometer_matrix)

    simulator = pq.SamplingSimulator(d=num_modes)
    result = simulator.execute(program, shots=num_shots)
    samples = result.samples

    print(f"Boson Sampling — {num_modes} modes, {total_photons} photons, {num_shots} shots\n")
    print(f"Input state: {input_state_vector}")
    print(f"  ({total_photons} photons in modes 0–{total_photons - 1}, vacuum in the rest)\n")

    # Show first 10 samples
    print("Sample output (photon counts per mode):")
    for i, sample in enumerate(samples[:10]):
        photon_counts = tuple(int(n) for n in sample)
        print(f"  Shot {i + 1:>3}: {photon_counts}  (total: {sum(photon_counts)})")
    if len(samples) > 10:
        print(f"  ... ({len(samples) - 10} more samples)")

    # Verify photon conservation
    conserved = all(sum(int(n) for n in s) == total_photons for s in samples)
    print(f"\nPhoton number conserved across all shots: {conserved}")

    # Count distinct output configurations
    unique_configs = len(set(tuple(int(n) for n in s) for s in samples))
    print(f"Distinct output configurations: {unique_configs}/{num_shots}")