#!/usr/bin/env python3
# label_resolver.py — pure semantic-target store + label->pose resolution
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Pure label->pose resolution for the go-to-target behavior (F35 / TF35 T05).

Holds the latest confirmed semantic targets (already converted from the typed
`SemanticTargetArray` msg at the ROS boundary — this module stays framework-free)
and resolves a label to a single goal pose. When a label has several confirmed
targets, the one nearest the robot wins; with no robot pose available it falls
back to the first match rather than blocking navigation. This is the typed
successor to nav_manager's `find_nearest_confirmed`, now carrying yaw.

`schema_version` gating and quaternion->yaw conversion happen at the node
boundary; this store trusts the `TargetPose` values it is given.
"""

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TargetPose:
    """One confirmed target, map frame. x_m/y_m in meters, yaw_rad in radians."""

    label: str
    target_id: str
    x_m: float
    y_m: float
    yaw_rad: float


def yaw_from_quaternion(z: float, w: float) -> float:
    """Planar (z-axis only) quaternion -> yaw. Matches the z=sin(yaw/2),
    w=cos(yaw/2) encoding used when building the drive goal."""
    return 2.0 * math.atan2(z, w)


@dataclass
class SemanticTargetStore:
    """Latest confirmed targets + nearest-match label resolution."""

    targets: list[TargetPose] = field(default_factory=list)

    def update(self, targets: list[TargetPose]):
        self.targets = list(targets)

    def resolve(
        self, label: str, robot_xy: tuple[float, float] | None
    ) -> TargetPose | None:
        """Nearest label-matching target to robot_xy, or None if no match.
        robot_xy None -> first match (no pose to rank by)."""
        matches = [target for target in self.targets if target.label == label]
        if not matches:
            return None
        if robot_xy is None:
            return matches[0]
        robot_x, robot_y = robot_xy

        def distance(target: TargetPose) -> float:
            return math.hypot(target.x_m - robot_x, target.y_m - robot_y)

        return min(matches, key=distance)
