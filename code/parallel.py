"""
Script to parallelize GI tests for faster checks

"""
import numpy as np
import pandas as pd
import multiprocessing as mp
import argparse

# Local imports
from utils import DATA, RES, read_data, GI_quantum_test, GI_classical_test

if __name__ == '__main__':
    # Setting up command line arguments
    argparser = argparse.ArgumentParser(
        description="Algorithm testing script",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argparser.add_argument('--algo', type=str, default="cls", help="Algorithm to use (vf2 - classical | ctqw - quantum)")
    argparser.add_argument('--fam', type=str, default="16-6-2-2", help="SRG family name (Check ./data/ directory for filenames)")
    argparser.add_argument('--p', type=int, default=1, help="Number of particles for CTQW")
    argparser.add_argument('--ptype', type=str, default="bos", help="Particle type (bos - Bosonic | ferm - fermionic)")
    # Following are based on values from the paper(s)
    argparser.add_argument('--time', type=float, default=1., help="Time at which U will be evaluated")
    argparser.add_argument('--tol', type=float, default=1e-10, help="Tolerance for comparison")

    # Processing args
    args = argparser.parse_args()
    algo = args.algo
    fam = args.fam
    p = args.p
    ptype = args.ptype
    time = args.time
    tol = args.tol

    # Number of parallel processes to run
    # NOTE: Using all CPU cores here, may cause system slow-down
    NUM_PROC = mp.cpu_count()

    FILES = {
        "16-6-2-2": "16-6-2-2.txt",
        "26-10-3-4": "26-10-3-4.g6",
        "36-14-4-6": "36-14-4-6.g6",
        "40-12-2-4": "40-12-2-4.txt"
    }
    if fam not in FILES:
        print(f"Error: SRG family {fam} not found. Check SRG families available in ./data/ or check parallel.py for all names. Exiting...")
        exit()

    # Reading in graphs
    graphs = read_data(DATA / FILES[fam])

    # Wrappers for pairwise tests
    def classical_on_pair(inds):
        g1, g2 = graphs[inds[0]], graphs[inds[1]]

        return inds[0], inds[1], GI_classical_test(g1, g2)

    def quantum_on_pair(inds):
        g1, g2 = graphs[inds[0]], graphs[inds[1]]

        return inds[0], inds[1], GI_quantum_test(g1, g2, p=p, ptype=ptype, time=time, tol=tol)

    if algo == "vf2":
        func = classical_on_pair
        save_path_mod = f"classical_test.csv"
    elif algo == "ctqw":
        func = quantum_on_pair
        save_path_mod = f"{p}-{ptype}_quantum_test.csv"
    else:
        print(f"Error: Algorithm {algo} not found. Only 'vf2' and 'ctqw' are supported. Exiting...")
        exit()

    # Pairs of indices
    pairs = np.transpose(np.triu_indices(graphs.shape[0], k=1))

    # Testing
    with mp.Pool(NUM_PROC) as proc:
        results = proc.map(func, pairs)

    # Saving to csv
    save_path = RES / f"{fam}"
    if not save_path.exists():
        save_path.mkdir(parents=True, exist_ok=True)
    save_path = save_path / save_path_mod

    df = pd.DataFrame(results)
    df.columns = ["Graph 1 Index", "Graph 2 Index", "Isomorphic?"]
    df.to_csv(save_path, index=None, encoding='utf-8')
    print(f"{algo} test on {fam} completed. Check {save_path}.")
