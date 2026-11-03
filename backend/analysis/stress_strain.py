import numpy as np
from backend.analysis.structure_analysis import persistent_cluster


def virial_stress(velocities, per_atom_virial, mobile, area):
    """Tensile-positive = negative conventional kinetic+configurational pressure.

    Per atom virial is half sum_j (r_i-r_j) outer F_ij. Unit mass/thickness.
    """
    kinetic = np.einsum('ni,nj->nij', velocities, velocities)
    return -(kinetic[mobile] + per_atom_virial[mobile]).sum(axis=0) / area


def detect_fracture(stresses, cluster_windows):
    # Fixed 3-point centered mean with edge replication, after full trajectory.
    s = np.convolve(np.pad(np.asarray(stresses), (1, 1), mode='edge'), np.ones(3)/3, mode='valid')
    peak = int(np.argmax(s))
    if s[peak] <= 1e-4 or peak >= len(s)-3:
        return peak, None, None
    for k in range(peak+1, len(s)-2):
        cluster = persistent_cluster(cluster_windows[k:k+3])
        if np.all(s[k:k+3] <= .65*s[peak]) and cluster:
            return peak, k, cluster
    return peak, None, None
