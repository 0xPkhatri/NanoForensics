"""Kinematic temperature diagnostics. These do not replace the raw acceptance gate."""
import numpy as np


def kinetic_diagnostics(q, velocities, mobile, bottom, top, reference_gauge, strain_rate):
    q=np.asarray(q);v=np.asarray(velocities)[mobile]
    n=len(v)
    if n<2:raise ValueError('At least two mobile atoms required')
    lower=float(np.mean(q[bottom,1]));upper=float(np.mean(q[top,1]))
    span=upper-lower
    if span<=0:raise ValueError('Positive gauge required')
    stream=np.zeros_like(v)
    stream[:,1]=(q[mobile,1]-.5*(lower+upper))*reference_gauge*strain_rate/span
    residual=v-stream
    # Fixed four material-height bins; subtract two fitted COM components per occupied bin.
    rows=np.clip(((q[mobile,1]-lower)/span*4).astype(int),0,3)
    local=v.copy();occupied=0
    for index in range(4):
        selected=rows==index
        if selected.any():
            local[selected]-=local[selected].mean(axis=0)
            occupied+=1
    dof=2*n-2*occupied
    return {'laboratory':float(np.sum(v*v)/(2*n)),
            'com_removed':float(np.sum((v-v.mean(axis=0))**2)/(2*n-2)),
            'affine_residual':float(np.sum(residual*residual)/(2*n)),
            'affine_stream_kinetic':float(np.sum(stream*stream)/(2*n)),
            'affine_cross_term':float(np.sum(stream*residual)/n),
            'local_flow_residual':float(np.sum(local*local)/dof) if dof>0 else None,
            'local_flow_dof':int(dof)}
