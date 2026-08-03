#!/usr/bin/env python3
# nav_intent_check.py — diagnostic: test dome_mission go-to-target on live stack
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Live diagnostic for the dome_mission go-to-target behavior (F35 / TF35 T05).

Reads the robot's map-frame pose from /amcl_pose, computes a target 50 cm to the
robot's left, publishes it as a typed SemanticTargetArray on /semantic/targets
(the schemaless /targets/confirmed JSON is gone), then publishes a navigation_go
intent on /intent. dome_mission resolves the label to that pose and drives via
Nav2 NavigateToPose.

Terminal-status verification (done/failed) is not asserted here: dome_mission has
no status topic yet (F08). Watch the robot / RViz, or the mission_node log, to
confirm arrival.

Usage: python3 tools/nav_intent_check.py
Requires: the dome_mission + Nav2 stack running, AMCL converged.
"""

import json
import math
import sys
import time

import rclpy
from builtin_interfaces.msg import Time
from dome_semantic_msgs.msg import SemanticTarget, SemanticTargetArray
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

LABEL = "chair"
GOAL_DIST_M = 0.50
SCHEMA_VERSION = 1


class NavIntentChecker(Node):
    def __init__(self):
        super().__init__("nav_intent_check")
        self.current_pose = None

        amcl_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped, "/amcl_pose", self.on_amcl_pose, amcl_qos
        )
        self.targets_pub = self.create_publisher(
            SemanticTargetArray, "/semantic/targets", 10
        )
        self.intent_pub = self.create_publisher(String, "/intent", 10)

    def on_amcl_pose(self, msg: PoseWithCovarianceStamped):
        self.current_pose = msg.pose.pose

    def spin_for(self, secs: float):
        deadline = time.time() + secs
        while time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)

    def wait_for_pose(self, timeout_sec: float = 10.0) -> bool:
        deadline = time.time() + timeout_sec
        while time.time() < deadline and self.current_pose is None:
            rclpy.spin_once(self, timeout_sec=0.1)
        return self.current_pose is not None

    def current_yaw(self) -> float:
        quaternion = self.current_pose.orientation
        return math.atan2(
            2.0 * (quaternion.w * quaternion.z + quaternion.x * quaternion.y),
            1.0 - 2.0 * (quaternion.y * quaternion.y + quaternion.z * quaternion.z),
        )

    def compute_target(self) -> tuple[float, float, float]:
        """Target 90 deg to the robot's left, GOAL_DIST_M away. Returns
        (x_m, y_m, yaw_rad) in the map frame; yaw faces along the offset."""
        pose = self.current_pose
        left_yaw = self.current_yaw() + math.pi / 2.0
        target_x = pose.position.x + GOAL_DIST_M * math.cos(left_yaw)
        target_y = pose.position.y + GOAL_DIST_M * math.sin(left_yaw)
        return (round(target_x, 3), round(target_y, 3), left_yaw)

    def send_target(self, x_m: float, y_m: float, yaw_rad: float):
        target = SemanticTarget()
        target.schema_version = SCHEMA_VERSION
        target.target_id = "diag-1"
        target.label = LABEL
        target.pose.position.x = x_m
        target.pose.position.y = y_m
        target.pose.orientation.z = math.sin(yaw_rad / 2.0)
        target.pose.orientation.w = math.cos(yaw_rad / 2.0)
        target.observation_count = 1
        target.last_seen = Time()
        array = SemanticTargetArray()
        array.header.frame_id = "map"
        array.header.stamp = self.get_clock().now().to_msg()
        array.targets = [target]
        self.wait_for_subscriber(self.targets_pub)
        for _ in range(3):
            self.targets_pub.publish(array)
            self.spin_for(0.1)

    def send_intent(self):
        msg = String()
        msg.data = json.dumps(
            {"name": "navigation_go", "source": "tool", "slots": {"label": LABEL}}
        )
        self.wait_for_subscriber(self.intent_pub)
        self.intent_pub.publish(msg)
        self.spin_for(0.2)

    def wait_for_subscriber(self, publisher, timeout_sec: float = 5.0):
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            if publisher.get_subscription_count() > 0:
                return
            rclpy.spin_once(self, timeout_sec=0.1)


def confirm_ready():
    print("\n" + "=" * 60)
    print("DIAGNOSTIC: dome_mission go-to-target check")
    print("=" * 60)
    print("\nWhat will happen:")
    print("  1. Read current robot pose from /amcl_pose")
    print("  2. Publish a typed SemanticTargetArray 50cm to the robot's left")
    print("  3. Publish a navigation_go intent; dome_mission drives there")
    print("\nWARNING: Ensure at least 1m clear space in ALL directions.")
    print("Requires: dome_mission + Nav2 stack running, AMCL converged.\n")
    return input("Proceed? [y/n]: ").strip().lower() == "y"


def main():
    if not confirm_ready():
        print("Aborted.")
        sys.exit(0)

    rclpy.init()
    node = NavIntentChecker()

    print("\n[1/3] Waiting for AMCL pose...")
    if not node.wait_for_pose(timeout_sec=10.0):
        print("FAIL: /amcl_pose not received within 10s — stack up, AMCL converged?")
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(1)
    pose = node.current_pose
    yaw = node.current_yaw()
    print(
        f"  pose: x={pose.position.x:.3f} y={pose.position.y:.3f} "
        f"yaw={math.degrees(yaw):.1f} deg"
    )

    target_x, target_y, target_yaw = node.compute_target()
    print(f"\n[2/3] Publishing SemanticTargetArray target: ({target_x}, {target_y})")
    node.send_target(target_x, target_y, target_yaw)
    print(f"  target subscribers: {node.targets_pub.get_subscription_count()}")

    print("\n[3/3] Publishing navigation_go intent...")
    print(f"  intent subscribers: {node.intent_pub.get_subscription_count()}")
    node.send_intent()

    print(
        "\nDONE: intent sent. Watch the robot / RViz / mission_node log for "
        "arrival (no status topic yet — F08)."
    )
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
