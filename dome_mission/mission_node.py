#!/usr/bin/env python3
# mission_node.py — ROS node: owns /intent, drives the mission FSM
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Mission-sequencing node (F35).

Owns `/intent` (TF35 T04): deserializes each payload, maps it to a mission
Intent (intent_parser), drives the pure MissionFsm, and executes the emitted
primitive commands. Command execution is currently logged only — the real
ExploreArea action client and Nav2 NavigateToPose wiring land in T05/T07. The
FSM and parser hold all the logic; this node is the thin ROS seam.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from dome_mission.intent_parser import parse_intent
from dome_mission.mission_fsm import Command, MissionFsm


class MissionNode(Node):
    def __init__(self):
        super().__init__("mission_node")
        self.fsm = MissionFsm()
        self.intent_sub = self.create_subscription(
            String, "/intent", self.on_intent, 10
        )
        self.get_logger().info("dome_mission mission_node up; owns /intent")

    def on_intent(self, msg: String):
        parsed = parse_intent(msg.data)
        if parsed is None:
            self.get_logger().warning(f"Malformed or unknown intent: {msg.data!r}")
            return
        commands = self.fsm.on_intent(
            parsed.intent, label=parsed.label, map_name=parsed.map_name
        )
        self.get_logger().info(
            f"intent {parsed.intent.name} -> state {self.fsm.state.name}"
        )
        for command in commands:
            self.execute(command)

    def execute(self, command: Command):
        """Run a primitive command. Stub: logs only until the action clients
        land (T05 drive-to-target, T07 explore wiring)."""
        payload = command.label or command.map_name
        detail = f" ({payload})" if payload else ""
        self.get_logger().info(f"pending execute {command.type.name}{detail}")


def main(args=None):
    rclpy.init(args=args)
    node = MissionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
