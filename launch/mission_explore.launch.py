#!/usr/bin/env python3
# mission_explore.launch.py — top-level: explore sub-stack + dome_mission front-end
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Top-level launch for the mission layer (F35 / TF35 T07).

Composes dome_nav's explore sub-stack (slam + Nav2 + explorer_manager, which now
exposes the ExploreArea action) and adds dome_mission's mission_node on top as
the sole `/intent` front-end. mission_node drives explore via ExploreArea and
go-to-target via Nav2 NavigateToPose; no `/intent` wiring reaches the explorer.

The dome_semantic / OAK-D sub-stack (TF33) is not composed here yet — it is
uncoded; add it once F33 Phase A lands so go-to-label has a live semantic map.
"""

from better_launch import BetterLaunch, launch_this


@launch_this(ui=True)
def mission_explore_launch(
    use_sim_time: str = "false",
    map_name: str = "",
):
    if not map_name:
        raise ValueError(
            "map_name is required: "
            "bl dome_mission mission_explore.launch.py --map_name <name>"
        )

    bl = BetterLaunch()

    bl.include(
        "dome_nav", "robot_explore.launch.py",
        map_name=map_name, use_sim_time=use_sim_time,
    )

    bl.node(
        "dome_mission",
        "mission_node",
        name="mission",
        ros_waittime=30.0,
    )
