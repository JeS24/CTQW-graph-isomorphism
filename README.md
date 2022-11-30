# STQM (P475) Term Paper
## Summary
In this term paper project, I have looked into ***Rudinger et al's paper [1] on the application of non-interacting multiparticle continuous-time quantum random walks (CTQWs) to the Graph Isomorphism (GI) problem for strongly regular graphs (SRGs)***. I have implemented their algorithm and tried to replicate their results and contrasted them with a classical GI test. I have also explored the empirical run-time and space complexity of their algorithm.

* A short report can be found in [`./report/`](./report/).
* Presentation slides are available at [`./slides/talk.pdf`](./slides/talk.pdf).
* Explicit results for the considered SRG families can be found in [`./code/results/`](./code/results/). Summaries are available under _Results_ below.
* The notebook at [`./code/example.ipynb`](./code/example.ipynb) can be perused for a quick overview of the code, while the full implementation is available in [`./code/utils.py`](./code/utils.py).
* Data considered for all tests can be found in the [`./code/data/`](./code/data/) directory.
* The tests were run using the [`./code/parallel.py`](./code/parallel.py) script for both classical and quantum cases. If you want to run the tests yourself, please review the command line arguments available in the script and run the script like so (these are specific examples with particular parameter values):
  * Classical: `python parallel.py --algo vf2 --fam 16-6-2-2`
  * Quantum: `python parallel.py --algo ctqw --fam 26-10-3-4 --p 1 --ptype bos`
* Notes about the parallelized script:
  * The calculations based on the CTQW can be highly compute and memory-heavy. Please review the _Results_ section below that talks about peak memory usage and run-time before running the code.
  * The classical test is primarily CPU bound with a minimal memory footprint as compared to the CTQW algorithm, which has been implemented in a way that trades off memory-inefficiency for time-efficiency.

## Setup
* The code here is written in Python 3.10.4.
* Set up a python virtual environment via `python -m venv <VENV_NAME>`.
* Activate it using `source <VENV_NAME>/bin/activate` on *nix and `./<VENV_NAME>/Scripts/activate` on Windows.
* Install requirements via `pip install -r requirements.txt`.

## Data

* Source for adjacency matrices in `txt` format: http://www.maths.gla.ac.uk/~es/srgraphs.php.
* Source for adjacency matrices in `graph6` format: http://users.cecs.anu.edu.au/~bdm/data/graphs.html.

I selected the following SRG families among several that were explored by the authors:
| SRG family | N(Graphs) | File format | Selection rationale |
|:-----------:|:-----------------:|:------------:|:--|
| (16, 6, 2, 2) | 2 | txt | Base case
| (26, 10, 3, 4) | 10 | graph6 | First case where authors reported a failure
| (36, 14, 4, 6) | 180 | graph6 | Large number of failures reported for this case
| (40, 12, 2, 4) | 28 | txt | Large $N$ with less number of comparisons with some reported failures

## Results

* ***Criterion: The classical & quantum algorithms should return `False` for all comparisons, since all graphs in the considered families are non-isomorphic.***
  * The classical algorithm successfully returned `False` for all comparisons.
  * All tests with $p = 1$ and $p = 2$ CTQW resulted in failures, i.e. non-isomorphic graphs were labelled as isomorphic, which is as expected. The $\Delta$ values were also observed to be very small at $\le 10^{-10}$, which is possibly near the noise floor for my implementation. This also shows the high multiplicities of Green's functions for 1 & 2-particle non-interacting CTQWs. See Sections III & IV in Gamble et al [2] for relevant analysis & discussion.
* Notes on the runs:
  * All the results below are from tests that were run in parallel on an HPC cluster with a 24-core CPU and 528 GB of RAM. Serial tests do not finish running in several cases.
  * I am considering CPU time below, since the tests were parallelized.
  * Also, note that the peak memory usage reported below is cumulative across all parallel processes. The reason for reporting _Peak_ instead of _Average_ usage is that the initial memory allocation, done mainly for the tensor products, is usually far higher than the allocation for subsequent processes like flattening, sorting and comparison.
  * **DNF** = Did Not Finish. These cases are entirely due to either the calculation taking too long to complete (>= 24 hours in CPU time) or the run crashing due to _OutOfMemory_ issues.

#### Results for the classical test using VF2
| SRG family | N(Graphs) | N(Comparisons) | Failures | Peak Mem Usage (in GB) | Avg. CPU Time (in s) |
|:-----------:|:-----------------:|:------------:|:----:|:----:|:----:|
| (16, 6, 2, 2) | 2 | 1 | 0 | 0.042 | 3.4
| (26, 10, 3, 4) | 10 | 45 | 0 | 1.176 | 15.1
| (36, 14, 4, 6) | 180 | 16_110  | 0 | 1.49 | 21732.3
| (40, 12, 2, 4) | 28 | 378 | 0 | 1.2 | 22915.7

#### Results for $p = 1$

| SRG family | N(Graphs) | N(Comparisons) | Boson failures | Fermion failures | Peak Mem Usage (in GB) | Avg. CPU Time (in s) |
|:-----------:|:-----------------:|:------------:|:----:|:----:|:----:|:----:|
| (16, 6, 2, 2) | 2 | 1 | 1 | 1 | 0.009 | 4.8
| (26, 10, 3, 4) | 10 | 45 | 45 | 45 | 1.39 | 21.4
| (36, 14, 4, 6) | 180 | 16_110 | 16_110 | 16_110 | 1.8 | 976
| (40, 12, 2, 4) | 28 | 378 | 378 | 378 | 1.53 | 90.1

#### Results for $p = 2$

| SRG family | N(Graphs) | N(Comparisons) | Boson failures | Fermion failures | Peak Mem Usage (in GB) | Avg. CPU Time (in s) |
|:-----------:|:-----------------:|:------------:|:----:|:----:|:----:|:----:|
| (16, 6, 2, 2) | 2 | 1 | 1 | 1 | 0.009 | 5.1
| (26, 10, 3, 4) | 10 | 45 | 45 | 45 | 1.92 | 35.4
| (36, 14, 4, 6) | 180 | 16_110 | **NA** | **NA** | 3.36 | **DNF** (> 2 hrs)
| (40, 12, 2, 4) | 28 | 378 | 378 | 378 | 2.73 | 930

#### Results for $p = 3$

| SRG family | N(Graphs) | N(Comparisons) | Boson failures | Fermion failures | Peak Mem Usage (in GB) | Avg. CPU Time (in s) |
|:-----------:|:-----------------:|:------------:|:----:|:----:|:----:|:----:|
| (16, 6, 2, 2) | 2 | 1 | 0 | 0 | 0.5 | 9.1
| (26, 10, 3, 4) | 10 | 45 | 1 | 1 | 112 | 2547.5
| (36, 14, 4, 6) | 180 | 16_110 | **NA** | **NA** | > 528 | **DNF** (Out of Memory)
| (40, 12, 2, 4) | 28 | 378 | **NA** | **NA** | > 528 | **DNF** (Out of Memory)

#### Results for $p = 4$

| SRG family | N(Graphs) | N(Comparisons) | Boson failures | Fermion failures | Peak Mem Usage (in GB) | Avg. CPU Time (in s) |
|:-----------:|:-----------------:|:------------:|:----:|:----:|:----:|:----:|
| (16, 6, 2, 2) | 2 | 1 | 0 | 0 | 156 | 525.1
| (26, 10, 3, 4) | 10 | 45 | **NA** | **NA** | > 528 | **DNF** (Out of Memory)
| (36, 14, 4, 6) | 180 | 16_110 | **NA** | **NA** | > 528 | **DNF** (Out of Memory)
| (40, 12, 2, 4) | 28 | 378 | **NA** | **NA** | > 528 | **DNF** (Out of Memory)

## Conclusions
1. The CTQW-based algorithm is extremely memory-inefficient.
2. I was able to replicate the results for $p = 1$ and $p = 2$ as well as the single failure observed for $p = 3$ for $\text{srg}(26, 10, 3, 4)$.
3. I also successfully verified that the evolution matrix and hence the graph signature is correct for $p = 1$, by comparing it with the explicit calculation done in [2] (Check [`./code/example.ipynb`](./code/example.ipynb)).

### Potential optimizations for the implementation
1. One obvious optimization can be storage of exponentiated matrices for all graphs. This will reduce the number of times the exponentiation is calculated for each comparison per graph.
2. Sorting is unnecessary for the quantum case, as long as the certificate or signature is not required. Also see [Wang et al](https://dx.doi.org/10.1088/1751-8113/48/11/115302), where they remove the sorting step (for a slightly different signature however).
3. Rudinger et al propose the use of binning to reduce the number of comparisons by exploiting the large number of degenerate list elements, which can be a good optimization for large graphs. However, I have followed the original algorithm and so, this is not implemented here.
4. From a purely `numpy`-implementation point of view, we can directly compare the Green's functions in pairs of evolution matrices without flattening, sorting or list-distance calculation. Although, this should at most result in a modest speedup or memory reduction.
5. On the subject of `numpy`/`scipy` algorithms, note that Rudinger et al found their noise floor to be `1e-6`. However, this is not a general floor and is not directly applicable to our case, since `scipy`'s matrix exponentiation approximation (and `numpy`'s functions) are more precise than the series approximation used for matrix exponentiation in their work. For instance, in an earlier work [2], they found $10^{-14} \le \Delta \le 10^{-9}$, which also reinforces the idea that the noise floor is implementation-specific.

## References
### Papers
1. Main paper: [Rudinger, K., Gamble, J., Wellons, M., Bach, E., Friesen, M., Joynt, R., & Coppersmith, S. (2012). Noninteracting multiparticle quantum random walks applied to the graph isomorphism problem for strongly regular graphs. Phys. Rev. A, 86, 022334.](https://link.aps.org/doi/10.1103/PhysRevA.86.022334)
2. Earlier work (source of the algorithm): [Gamble, J., Friesen, M., Zhou, D., Joynt, R., & Coppersmith, S. (2010). Two-particle quantum walks applied to the graph isomorphism problem. Phys. Rev. A, 81, 052313.](https://link.aps.org/doi/10.1103/PhysRevA.81.052313)
3. A specific optimization: [Huiquan Wang, Junjie Wu, Xuejun Yang, & Xun Yi (2015). A graph isomorphism algorithm using signatures computed via quantum walk search model. Journal of Physics A: Mathematical and Theoretical, 48(11), 115302.](https://dx.doi.org/10.1088/1751-8113/48/11/115302)

### Parts of code
* [Classical test of Graph Isomorphism using VF2 algorithm via NetworkX](https://networkx.org/documentation/stable/reference/algorithms/isomorphism.vf2.html)
* [Matrix exponentiation using scipy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.expm.html)
