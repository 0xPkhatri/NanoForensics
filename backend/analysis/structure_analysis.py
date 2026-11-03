"""Observable topology only. Graphs are reference-adjacency, never label-based."""
import numpy as np
R0 = 2 ** (1 / 6)


def distances(q):
    return np.linalg.norm(q[:, None, :] - q[None, :, :], axis=2)


def reference_graph(q):
    d = distances(q)
    return (d > 0) & (d < 1.35 * R0)


def rupture(q, graph, mobile):
    d = distances(q)
    current = (d > 0) & (d < 1.35 * R0)
    z = current.sum(axis=1)
    loss = np.maximum(0, graph.sum(axis=1) - z)
    severed = (graph & (d > 1.65)).sum(axis=1)
    active = (severed >= 2) & (loss >= 1) & (z <= 4) & mobile
    remaining = set(np.flatnonzero(active).tolist())
    clusters = []
    while remaining:
        found = {remaining.pop()}
        frontier = set(found)
        while frontier:
            nxt = {j for i in frontier for j in np.flatnonzero(graph[i]) if j in remaining}
            remaining -= nxt
            found |= nxt
            frontier = nxt
        clusters.append(found)
    return z, loss, severed, clusters


def persistent_cluster(windows, size=4):
    """One shared reference-connected identity must survive all three windows."""
    if len(windows) < 3:
        return None
    for a in windows[0]:
        if len(a) < size:
            continue
        for b in windows[1]:
            for c in windows[2]:
                if len(b) >= size and len(c) >= size and a & b & c:
                    return a
    return None


def localize(cluster, reference):
    if not cluster:
        return 'distributed'
    x = reference[list(cluster), 0].mean()
    lo, hi = reference[:, 0].min(), reference[:, 0].max()
    return 'surface_left' if x < lo + .22 * (hi-lo) else 'surface_right' if x > hi-.22*(hi-lo) else 'interior'
