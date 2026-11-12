"""Stage 1 policies: predetermined scripts only. No reactive strategies here yet."""

import numpy as np


class Scripted:
    """Plays velocities[k] at the agent's k-th decision.

    Running off the end raises: a script that's too short is a bug in the
    experiment setup, and silently holding the last velocity would hide it.
    """

    def __init__(self, velocities):
        self.velocities = [np.asarray(v, dtype=float) for v in velocities]

    def __call__(self, obs):
        if obs.k >= len(self.velocities):
            raise IndexError(f"script for {obs.role} exhausted at decision {obs.k} (t={obs.t})")
        return self.velocities[obs.k]


class Constant:
    def __init__(self, velocity):
        self.velocity = np.asarray(velocity, dtype=float)

    def __call__(self, obs):
        return self.velocity
