"""
This file contains all the necessary code for implementing the algorithm

"""
from pathlib import Path
import numpy as np
import scipy as sc
import networkx as nx

# Global path variables
DATA = Path('./data/')
RES = Path('./results/')

"""
General utilities

"""
def read_txt(path):
    """
    Reads text file and returns numpy array containing all graphs

    Parameters
    ----------
    path : pathlib.Path
        Path to data

    Returns
    -------
    numpy.ndarray

    """
    lns = path.read_text().splitlines()
    first_line = lns[0]
    dim = int(first_line[first_line.index("dim=") + 4:first_line.index("dim=") + 6])
    # deg = int(first_line[first_line.index("degree=") + 7])
    # lmd = int(first_line[first_line.index("lambda=") + 7])
    # mu = int(first_line[first_line.index("mu=") + 3])

    long_text = "TOTAL NUMBER OF STRONGLY REGULAR GRAPHS = "
    NUM = 0
    _1D = []
    for l in lns:
        if l.startswith("0") or l.startswith("1"):
            l2 = ','.join(l)
            _1D.append(np.fromstring(l2, sep=','))

        if long_text in l:
            NUM = int(l[len(long_text):])

    all_graphs = np.c_[_1D]

    return all_graphs.reshape(NUM, dim, dim)

def read_graph6(path):
    """
    Reads graph6 file and returns adjacency matrices as numpy arrays

    Parameters
    ----------
    path : pathlib.Path
        Path to data
 
    Returns
    -------
    numpy.ndarray

    """
    Gs = nx.read_graph6(path)

    if not isinstance(Gs, list):
        G = nx.to_numpy_array(Gs)
        return G.reshape(1, *G.shape)

    Gs_np = []
    for G in Gs:
        Gs_np.append(nx.to_numpy_array(G))

    return np.c_[Gs_np]

def read_data(path):
    """
    General data-reader

    Parameters
    ----------
    path : pathlib.Path
        Path to data
 
    Returns
    -------
    numpy.ndarray

    """
    path = Path(path)
    if path.suffix not in [".g6", ".txt"]:
        print(f"Error: {path.suffix} not supported. Check file path. Only .g6 and .txt files are supported. Exiting...")
        return None

    if path.suffix == ".g6":
        return read_graph6(path)

    return read_txt(path)

def draw_graph(adj):
    """
    Draws graph using adjacency matrix

    Parameters
    ----------
    adj : numpy.ndarray
        Adjacency matrix of the graph

    """
    G = nx.from_numpy_matrix(adj)
    nx.draw(G)

def mat_exp(M, ord=20):
    """
    Naive algorithm, using Taylor series to approximate matrix exponentiation
    DONTUSE / Prefer scipy.linalg.expm (same results at higher order, but scipy's is faster)

    """
    mp = np.linalg.matrix_power
    fac = np.math.factorial

    sum = 0
    for i in range(ord):
        sum += mp(M, i) / fac(i)

    return sum

def tensor_prod(n=1):
    """
    Returns a function that calculates the matrix Tensor product (Kronecker product or \odot) via recursive function composition

    Parameters
    ----------
    n : int
        Number of times to take the Kronecker product
        Equivalent to ``M^\odot n``
        n == 1 => Identity or no tensor product
        For usage, see `GI_quantum_test()` below.

    Returns
    -------
    callable
        Function that calculates the Tensor product
        n == 1 => Identity or no tensor product

    """
    if n == 1:
        return lambda x, y: x # Identity
    elif n == 2:
        return np.kron # M \odot M
    # Recursively calculate M \odot ... \odot M | "Normal ordering" (left to right)
    return lambda M1, M2: np.kron(M1, tensor_prod(n - 1)(M1, M2))

"""
Classical Graph Isomorphism test

"""
def GI_classical_test(adj_G1, adj_G2):
    """
    Tests if two graphs are isomorphic using the classical VF2 algorithm as implemented in NetworkX

    Parameters
    ----------
    adj_G1 : numpy.ndarray
        Adjacency matrix of Graph 1
    adj_G2 : numpy.ndarray
        Adjacency matrix of Graph 2

    Returns
    -------
    bool
        Boolean result of the test

    """
    G1 = nx.from_numpy_matrix(adj_G1)
    G2 = nx.from_numpy_matrix(adj_G2)
    GM = nx.algorithms.isomorphism.GraphMatcher(G1, G2)

    return GM.is_isomorphic() #, GM.mapping

def classical_test(graphs, family):
    """
    Tests if all graphs in the given array (SRG family)are isomorphic 
    using the classical VF2 algorithm as implemented in NetworkX
    Saves the results in a csv file

    Parameters
    ----------
    graphs : numpy.ndarray
        Array of adjacency matrices
    family : str
        SRG family name

    Returns
    -------
    numpy.ndarray
        Contains the indices & result of the test (0 - False / Non-isomorphic | 1 - True / Isomorphic)

    """
    pairs = np.transpose(np.triu_indices(graphs.shape[0], k=1))
    class_res = np.empty((0, 3), int)
    for p in pairs:
        class_res = np.append(class_res, [[p[0], p[1], GI_classical_test(graphs[p[0]], graphs[p[1]])]], axis=0)

    save_path = RES / f"{family}"
    if not save_path.exists():
        save_path.mkdir(parents=True, exist_ok=True)
    with open(save_path / "classical_test.csv", 'w') as f:
        np.savetxt(f, class_res, delimiter=',', fmt='%d')

    return class_res

"""
Quantum Graph Isomorphism test using non-interacting CTQW

"""
def GI_quantum_algo(adj_G1, adj_G2, p=3, ptype="bos", time=1.):
    """
    Returns list distance (`\Delta`) between graph signatures for two graphs, using the CTQW algorithm as 
    outlined first in Gamble et al (2010) [1]_ & then in Rudinger et al (2012) [2]_.
    Equation numbers are from [2]_.

    Parameters
    ----------
    adj_G1 : numpy.ndarray
        Adjacency matrix of Graph 1
    adj_G2 : numpy.ndarray
        Adjacency matrix of Graph 2
    p : int
        Number of particles in the QW
        Defaults to 3
    ptype : str
        "ferm" for ferminonic walk & "bos" for bosonic walk
        Defaults to "bos"
    time : float
        Time at which U is to be calculated
        Defaults to 1 (From Rudinger et al [2]_)
        Optional, but small values recommended to avoid numerical issues with matrix exponentiation

    Returns
    -------
    delta : float
        Distance between the lists
        delta = 0 => Isomorphic & delta != 0 => Non-isomorphic graphs
 
    References
    ----------
    .. [1] Gamble, J., Friesen, M., Zhou, D., Joynt, R., & Coppersmith, S. (2010). Two-particle quantum walks applied to the graph isomorphism problem. Phys. Rev. A, 81, 052313.
    .. [2] Rudinger, K., Gamble, J., Wellons, M., Bach, E., Friesen, M., Joynt, R., & Coppersmith, S. (2012). Noninteracting multiparticle quantum random walks applied to the graph isomorphism problem for strongly regular graphs. Phys. Rev. A, 86, 022334.

    """    
    # Matrix exponentiation (Padé approximation)
    ex = sc.linalg.expm

    # Settings proper coefficient depending on particle-type
    if ptype not in ["bos", "ferm"]:
        print("Error: Incorrect particle type. Input 'bos' for bosonic walk and 'ferm' for fermionic walk. Exiting...")
        return None
    fac = 1 if ptype == "bos" else -1

    # 1. Calculate complex evolution matrices for the two graphs
    # p = 1 | Single particle evolution matrix (Eq. 8)
    U1 = ex(fac * 1j * adj_G1 * time)
    U2 = ex(fac * 1j * adj_G2 * time)
    # Taking tensor product to get multi-particle evolution matrices (Eq. 10)
    U1 = tensor_prod(n=p)(U1, U1)
    U2 = tensor_prod(n=p)(U2, U2)

    # 2. Take the magnitude of each element
    U1 = np.abs(U1)
    U2 = np.abs(U2)

    # 3. Collect real entries in lists
    U1 = U1.flatten()
    U2 = U2.flatten()

    # 4. Sort the lists | Also see: Wang et al - https://dx.doi.org/10.1088/1751-8113/48/11/115302
    U1.sort()
    U2.sort()

    # 5. Calculate list distance
    delta = np.sum(np.abs(U1 - U2))

    return delta

def GI_quantum_test(adj_G1, adj_G2, p=3, ptype="bos", time=1., tol=1e-10):
    """
    Tests if two graphs are isomorphic using the algorithm in `GI_quantum_algo()` above

    Parameters
    ----------
    adj_G1 : numpy.ndarray
        Adjacency matrix of Graph 1
    adj_G2 : numpy.ndarray
        Adjacency matrix of Graph 2
    p : int
        Number of particles in the QW
        Defaults to 3
    ptype : str
        "ferm" for ferminonic walk & "bos" for bosonic walk
        Defaults to "bos"
    time : float
        Time at which U is to be calculated
        Defaults to 1. (From Rudinger et al)
        Optional, but small values recommended to avoid numerical issues with matrix exponentiation
    tol : float
        Tolerance for the comparing list distance with 0
        Defaults to 1e-10

    Returns
    -------
    bool
        Boolean result of the test

    """
    delta = GI_quantum_algo(adj_G1, adj_G2, p=p, ptype=ptype, time=time)

    # Checking if delta is 0 (close to 0, closeness specified by `tol` value)
    res = np.allclose(delta, 0., rtol=tol, atol=tol)

    return res #, delta

def quantum_test(graphs, family, p=3, ptype="bos", time=1., tol=1e-10):
    """
    Tests if all graphs in the given array (SRG family) are isomorphic 
    using the algorithm in `GI_quantum_algo()` above
    Saves the results in a csv file

    Parameters
    ----------
    graphs : numpy.ndarray
        Array of adjacency matrices
    family : str
        SRG family name
    p : int
        Number of particles in the QW
        Defaults to 3
    ptype : str
        "ferm" for ferminonic walk & "bos" for bosonic walk
        Defaults to "bos"
    time : float
        Time at which U is to be calculated
        Defaults to 1 (From Rudinger et al)
        Optional, but small values recommended to avoid numerical issues with matrix exponentiation
    tol : float
        Tolerance for the comparing list distance with 0
        Defaults to 1e-10

    Returns
    -------
    numpy.ndarray
        Contains the indices & result of the test (0 - False / Non-isomorphic | 1 - True / Isomorphic)

    """
    pairs = np.transpose(np.triu_indices(graphs.shape[0], k=1))
    class_res = np.empty((0, 3), int)
    for pa in pairs:
        class_res = np.append(
            class_res, 
            [[pa[0], pa[1], GI_quantum_test(graphs[pa[0]], graphs[pa[1]], p=p, ptype=ptype, time=time)]],
            axis=0
        )

    save_path = RES / f"{family}"
    if not save_path.exists():
        save_path.mkdir(parents=True, exist_ok=True)
    with open(save_path / f"{p}-{ptype}_quantum_test.csv", 'w') as f:
        np.savetxt(f, class_res, delimiter=',', fmt='%d')

    return class_res
