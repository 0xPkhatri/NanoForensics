"""Observable row fit and topology-based missing-component reconstruction."""
import numpy as np
from scipy.spatial import cKDTree
from backend.models.schemas import InterventionType


def missing_components(coordinates):
    q=np.asarray(coordinates,float)
    tree=cKDTree(q)
    a=float(np.median(tree.query(q,k=2)[0][:,1]))
    rows=np.rint((q[:,1]-q[:,1].min())/(a*np.sqrt(3)/2)).astype(int)
    lo,hi=q.min(axis=0),q.max(axis=0)
    candidates=[]
    for row in sorted(set(rows)):
        if row<2 or row>rows.max()-2:continue
        pts=q[rows==row]
        phase=np.angle(np.exp(2j*np.pi*pts[:,0]/a).mean())/(2*np.pi)
        origin=(phase%1)*a
        for index in range(int(np.floor((lo[0]-origin)/a)),int(np.ceil((hi[0]-origin)/a))+1):
            p=np.array([origin+index*a,float(np.median(pts[:,1]))])
            if not lo[0]-.05*a<=p[0]<=hi[0]+.05*a:continue
            if tree.query(p)[0]<.55*a:continue
            if len(tree.query_ball_point(p,1.4*a))>=3:candidates.append(p)
    if not candidates:return []
    sites=np.array(candidates)
    graph=np.linalg.norm(sites[:,None]-sites[None,:],axis=2)<1.35*a
    remaining=set(range(len(sites)));components=[]
    while remaining:
        component={remaining.pop()};frontier=set(component)
        while frontier:
            nxt={j for i in frontier for j in np.flatnonzero(graph[i]) if j in remaining}
            remaining-=nxt;component|=nxt;frontier=nxt
        positions=sites[sorted(component)]
        edge=bool(np.any(positions[:,0]<=lo[0]+.75*a) or np.any(positions[:,0]>=hi[0]-.75*a))
        components.append({'boundary_connected':edge,'sites':positions.tolist()})
    return components


def reconstruct(specimen,intervention):
    out=specimen.model_copy(deep=True)
    boundary=intervention==InterventionType.SMOOTH_SURFACE_NOTCH
    if intervention not in [InterventionType.HEAL_INTERIOR_VACANCY,InterventionType.SMOOTH_SURFACE_NOTCH]:raise ValueError('Study permits only registered geometric interventions')
    components=[c for c in missing_components(out.coordinates) if c['boundary_connected']==boundary]
    positions=[p for c in components for p in c['sites']]
    ids=list(range(max(out.atom_ids)+1,max(out.atom_ids)+1+len(positions)))
    out.coordinates.extend(positions);out.atom_ids.extend(ids)
    return out,{'status':'APPLIED' if positions else 'NO_APPLICABLE_EDIT','components':components,'inferred_locations':positions,'inserted_atom_ids':ids,'removed_atom_ids':[],'geometry_algorithm':'observable-component-fit-v1'}
