#!/usr/bin/env python3
# mission_node.py — ROS node: owns /intent, drives the mission FSM
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Mission-sequencing node (F35).

Owns `/intent` (TF35 T04): deserializes each payload, maps it to a mission Intent
(intent_parser), drives the pure MissionFsm, and executes the emitted primitive
commands. The FSM/parser/resolver hold the logic; this node is the ROS seam.

Go-to-target (TF35 T05): subscribes the typed `SemanticTargetArray`, keeps a pure
`SemanticTargetStore`, and on a DRIVE_TO_TARGET command resolves the label to a
map-frame pose (nearest to the robot) and drives there via Nav2 `NavigateToPose`
directly — no dome_nav hop. A missing label fails the behavior cleanly
(on_done(DRIVE_FAILED)) so the FSM returns to IDLE.

Explore (START_EXPLORE / CANCEL_EXPLORE) drives dome_nav's ExploreArea action;
the terminal outcome feeds back into the FSM (on_done). Go-to-target uses Nav2
NavigateToPose directly (above).
"""

import math

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String

from dome_nav_msgs.action import ExploreArea
from dome_semantic_msgs.msg import SemanticTargetArray

from dome_mission.intent_parser import parse_intent
from dome_mission.label_resolver import (
    SemanticTargetStore,
    TargetPose,
    yaw_from_quaternion,
)
from dome_mission.mission_fsm import Command, CommandType, MissionFsm, Outcome

EXPECTED_SCHEMA_VERSION = 1
SEMANTIC_TARGETS_TOPIC = "/semantic/targets"

# ExploreArea result outcome (uint8) -> mission Outcome.
EXPLORE_OUTCOMES = {
    ExploreArea.Result.EXPLORED_DONE: Outcome.EXPLORED_DONE,
    ExploreArea.Result.STOPPED: Outcome.STOPPED,
    ExploreArea.Result.NO_TARGETS_BLOCKED: Outcome.NO_TARGETS_BLOCKED,
}


class MissionNode(Node):
    def __init__(self):
        super().__init__("mission_node")
        self.fsm = MissionFsm()
        self.store = SemanticTargetStore()
        self.robot_xy = None
        self.drive_goal_handle = None
        self.explore_goal_handle = None
        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.explore_client = ActionClient(self, ExploreArea, "explore_area")
        self.intent_sub = self.create_subscription(
            String, "/intent", self.on_intent, 10
        )
        self.targets_sub = self.create_subscription(
            SemanticTargetArray, SEMANTIC_TARGETS_TOPIC, self.on_semantic_targets, 10
        )
        self.amcl_sub = self.create_subscription(
            PoseWithCovarianceStamped, "/amcl_pose", self.on_amcl_pose, 10
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

    def on_semantic_targets(self, msg: SemanticTargetArray):
        """Ingest the typed semantic map: gate schema_version, convert each Pose
        to a pure TargetPose (yaw from the planar quaternion), refresh the store."""
        kept = []
        dropped = 0
        for target in msg.targets:
            if target.schema_version != EXPECTED_SCHEMA_VERSION:
                dropped += 1
                continue
            yaw_rad = yaw_from_quaternion(
                target.pose.orientation.z, target.pose.orientation.w
            )
            kept.append(
                TargetPose(
                    label=target.label,
                    target_id=target.target_id,
                    x_m=target.pose.position.x,
                    y_m=target.pose.position.y,
                    yaw_rad=yaw_rad,
                )
            )
        if dropped:
            self.get_logger().warning(
                f"Dropped {dropped} target(s) with schema_version != "
                f"{EXPECTED_SCHEMA_VERSION}"
            )
        self.store.update(kept)

    def on_amcl_pose(self, msg: PoseWithCovarianceStamped):
        position = msg.pose.pose.position
        self.robot_xy = (position.x, position.y)

    def execute(self, command: Command):
        handlers = {
            CommandType.DRIVE_TO_TARGET: lambda: self.drive_to_label(command.label),
            CommandType.CANCEL_DRIVE: self.cancel_drive,
            CommandType.START_EXPLORE: lambda: self.start_explore(command.map_name),
            CommandType.CANCEL_EXPLORE: self.cancel_explore,
        }
        handlers[command.type]()

    def start_explore(self, map_name: str):
        if not self.explore_client.server_is_ready():
            self.get_logger().error("ExploreArea server unavailable")
            self.fsm.on_done(Outcome.STOPPED)
            return
        goal = ExploreArea.Goal()
        goal.map_name = map_name
        send_future = self.explore_client.send_goal_async(goal)
        send_future.add_done_callback(self.on_explore_response)
        self.get_logger().info(f"Exploring (map_name={map_name!r})")

    def on_explore_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warning("Explore goal rejected")
            self.fsm.on_done(Outcome.STOPPED)
            return
        self.explore_goal_handle = handle
        handle.get_result_async().add_done_callback(self.on_explore_result)

    def on_explore_result(self, future):
        self.explore_goal_handle = None
        outcome = EXPLORE_OUTCOMES.get(future.result().result.outcome, Outcome.STOPPED)
        self.fsm.on_done(outcome)

    def cancel_explore(self):
        if self.explore_goal_handle is not None:
            self.explore_goal_handle.cancel_goal_async()
            self.explore_goal_handle = None

    def drive_to_label(self, label: str):
        target = self.store.resolve(label, self.robot_xy)
        if target is None:
            self.get_logger().warning(f"No confirmed target for label {label!r}")
            self.fsm.on_done(Outcome.DRIVE_FAILED)
            return
        if not self.nav_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().error("NavigateToPose server unavailable")
            self.fsm.on_done(Outcome.DRIVE_FAILED)
            return
        goal = NavigateToPose.Goal()
        goal.pose = self.goal_pose(target)
        send_future = self.nav_client.send_goal_async(goal)
        send_future.add_done_callback(self.on_goal_response)
        self.get_logger().info(f"Driving to {label!r} at ({target.x_m}, {target.y_m})")

    def goal_pose(self, target: TargetPose) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = target.x_m
        pose.pose.position.y = target.y_m
        pose.pose.orientation.z = math.sin(target.yaw_rad / 2.0)
        pose.pose.orientation.w = math.cos(target.yaw_rad / 2.0)
        return pose

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warning("Drive goal rejected")
            self.fsm.on_done(Outcome.DRIVE_FAILED)
            return
        self.drive_goal_handle = handle
        handle.get_result_async().add_done_callback(self.on_drive_result)

    def on_drive_result(self, future):
        self.drive_goal_handle = None
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.fsm.on_done(Outcome.ARRIVED)
        else:
            self.fsm.on_done(Outcome.DRIVE_FAILED)

    def cancel_drive(self):
        if self.drive_goal_handle is not None:
            self.drive_goal_handle.cancel_goal_async()
            self.drive_goal_handle = None


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
