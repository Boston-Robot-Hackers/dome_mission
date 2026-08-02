#!/usr/bin/env python3
# mission_explore.launch.py — top-level: explore sub-stack + dome_mission front-end
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Top-level launch for the mission layer.

Composes dome_nav's explore sub-stack with dome_mission's mission_node, the
sole `/intent` front-end (drives explore via ExploreArea, go-to-target via
Nav2 NavigateToPose).

`sim_mode` picks the dome_nav sub-stack: `robot_explore.launch.py` (real
robot) or `sim_nav_full.launch.py` (Gazebo + slam + Nav2 + explorer). It is
not named `use_sim_time` because better_launch's reserved `--use-sim-time`
global silently overrides a same-named parameter via click's destination
normalization; the two included launch files set the real ROS `use_sim_time`
internally.

dome_semantic / OAK-D is not composed here yet.
"""

from better_launch import BetterLaunch, launch_this


@launch_this(ui=True)
def mission_explore_launch(
    sim_mode: str = "false",
    map_name: str = "",
    world_name: str = "",
    urdf_name: str = "minimal_sim.urdf",
):
    if not map_name:
        raise ValueError(
            "map_name is required: "
            "bl dome_mission mission_explore.launch.py --map_name <name>"
        )

    sim_mode = {
        "true": True,
        "t": True,
        "1": True,
        "yes": True,
        "false": False,
        "f": False,
        "0": False,
        "no": False,
    }[sim_mode.strip().lower()]

    bl = BetterLaunch()
    print(
        f"mission_explore.launch.py: sim_mode={sim_mode}, map_name={map_name}, world_name={world_name}, urdf_name={urdf_name}"
    )
    if sim_mode:
        bl.include(
            "dome_nav",
            "sim_nav_full.launch.py",
            map_name=map_name,
            world_name=world_name,
            urdf_name=urdf_name,
        )
    else:
        bl.include(
            "dome_nav",
            "robot_explore.launch.py",
            map_name=map_name,
            use_sim_time=str(sim_mode).lower(),
        )

    bl.node(
        "dome_mission",
        "mission_node",
        name="mission",
        ros_waittime=30.0,
    )
