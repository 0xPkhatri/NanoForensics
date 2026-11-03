"""Triangular (six-neighbor) 2D lattice and blind geometric reconstruction."""
import numpy as np
from scipy.spatial import cKDTree
from backend.models.schemas import SpecimenInput, InterventionType, InterventionParameters
from backend.analysis.structure_analysis import R0


def hex_lattice(nx=12, ny=12, spacing=R0):
    return np.array([[(i+.5*(j%2))*spacing, j*spacing*np.sqrt(3)/2] for j in range(ny) for i in range(nx)])


def infer_missing_sites(coordinates, interior=True):
    """Fit visible row spacing and offsets. Fill only gaps inside the observed hull.

    No pristine site IDs or ground truth needed. This targets aligned benchmark
    crystals; rotated/disordered specimens can legitimately have no applicable edit.
    """
    q = np.asarray(coordinates, float)
    tree = cKDTree(q)
    nearest = tree.query(q, k=2)[0][:, 1]
    a = float(np.median(nearest))
    rows = np.rint((q[:, 1]-q[:, 1].min())/(a*np.sqrt(3)/2)).astype(int)
    candidates = []
    lo, hi = q.min(axis=0), q.max(axis=0)
    for row in sorted(set(rows)):
        pts = q[rows == row]
        if row < 2 or row > rows.max()-2:
            continue
        y = float(np.median(pts[:, 1]))
        # Phase from observed row; robust nearest-lattice projection.
        origin = float(np.median(pts[:, 0] - np.rint(pts[:, 0]/a)*a))
        for k in range(int(np.floor((lo[0]-origin)/a)), int(np.ceil((hi[0]-origin)/a))+1):
            x = origin + k*a
            if not lo[0]-.05*a <= x <= hi[0]+.05*a:
                continue
            p = np.array([x, y])
            if tree.query(p)[0] < .55*a:
                continue
            neighbors = tree.query_ball_point(p, 1.4*a)
            is_interior = lo[0]+1.3*a < x < hi[0]-1.3*a
            if is_interior == interior and len(neighbors) >= (3 if interior else 2):
                candidates.append(p)
    return np.array(candidates).reshape(-1, 2)


def transform(specimen: SpecimenInput, intervention: InterventionType, parameters=None):
    params = parameters or InterventionParameters()
    out = specimen.model_copy(deep=True)
    trace = {'status': 'APPLIED', 'inferred_locations': [], 'inserted_atom_ids': []}
    if intervention in (InterventionType.HEAL_INTERIOR_VACANCY, InterventionType.SMOOTH_SURFACE_NOTCH):
        sites = infer_missing_sites(out.coordinates, intervention == InterventionType.HEAL_INTERIOR_VACANCY)
        if not len(sites):
            trace['status'] = 'NO_APPLICABLE_EDIT'
        else:
            ids = list(range(max(out.atom_ids)+1, max(out.atom_ids)+1+len(sites)))
            out.coordinates.extend(sites.tolist())
            out.atom_ids.extend(ids)
            trace.update(inferred_locations=sites.tolist(), inserted_atom_ids=ids)
    elif intervention == InterventionType.NORMALIZE_STRAIN_RATE:
        out.protocol.strain_rate = params.target_strain_rate or .05
    elif intervention == InterventionType.NORMALIZE_TEMPERATURE:
        out.protocol.temperature = params.target_temperature or .05
    if intervention != InterventionType.REPEAT_REPLICATE_SEEDS and out.model_dump() == specimen.model_dump():
        trace['status'] = 'NO_APPLICABLE_EDIT'
    return out, trace
