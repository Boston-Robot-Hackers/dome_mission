#!/usr/bin/env python3
# test_mission_node.py — TF35 T04: /intent payloads drive the node's FSM
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import json
import math

import pytest
import rclpy
from std_msgs.msg import String

from dome_semantic_msgs.msg import SemanticTarget, SemanticTargetArray

from dome_mission.label_resolver import TargetPose
from dome_mission.mission_fsm import State
from dome_mission.mission_node import MissionNode


@pytest.fixture(scope="module", autouse=True)
def ros():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    mission = MissionNode()
    yield mission
    mission.destroy_node()


def intent_msg(name, slots=None):
    msg = String()
    msg.data = json.dumps({"name": name, "source": "cli", "slots": slots or {}})
    return msg


def test_intent_subscription_exists(node):
    # Exactly one /intent handler lives here (single-handler invariant, T04).
    assert node.intent_sub.topic_name == "/intent"


def test_exploration_start_drives_fsm(node):
    node.on_intent(intent_msg("exploration_start"))
    assert node.fsm.state is State.EXPLORING


def test_stop_returns_idle(node):
    node.on_intent(intent_msg("exploration_start"))
    node.on_intent(intent_msg("exploration_stop"))
    assert node.fsm.state is State.IDLE


def test_cancel_returns_idle(node):
    # No live Nav2 server here, so an unresolved go-to-target settles at IDLE;
    # the GOING_TO_TARGET transition itself is covered by the pure FSM tests.
    node.on_intent(intent_msg("navigation_go", {"label": "can"}))
    node.on_intent(intent_msg("navigation_cancel"))
    assert node.fsm.state is State.IDLE


def test_malformed_intent_is_ignored(node):
    bad = String()
    bad.data = "{not json"
    node.on_intent(bad)
    assert node.fsm.state is State.IDLE


# --- T05 go-to-target: semantic ingest + resolution ---

def semantic_target(label, x, y, yaw=0.0, schema_version=1, target_id="t"):
    target = SemanticTarget()
    target.schema_version = schema_version
    target.target_id = target_id
    target.label = label
    target.pose.position.x = x
    target.pose.position.y = y
    target.pose.orientation.z = math.sin(yaw / 2.0)
    target.pose.orientation.w = math.cos(yaw / 2.0)
    return target


def target_array(targets):
    array = SemanticTargetArray()
    array.targets = targets
    return array


def test_ingest_populates_store(node):
    node.on_semantic_targets(target_array([
        semantic_target("can", 1.0, 2.0, target_id="a"),
        semantic_target("cup", 3.0, 4.0, target_id="b"),
    ]))
    assert len(node.store.targets) == 2
    assert node.store.resolve("can", None).target_id == "a"


def test_ingest_converts_pose_and_yaw(node):
    node.on_semantic_targets(target_array([
        semantic_target("can", 1.5, -2.5, yaw=math.pi / 2),
    ]))
    resolved = node.store.resolve("can", None)
    assert resolved.x_m == pytest.approx(1.5)
    assert resolved.y_m == pytest.approx(-2.5)
    assert resolved.yaw_rad == pytest.approx(math.pi / 2)


def test_ingest_drops_wrong_schema_version(node):
    node.on_semantic_targets(target_array([
        semantic_target("can", 1.0, 2.0, schema_version=99),
    ]))
    assert node.store.targets == []


def test_go_to_unknown_label_fails_cleanly(node):
    node.on_semantic_targets(target_array([semantic_target("can", 1.0, 2.0)]))
    node.on_intent(intent_msg("navigation_go", {"label": "ghost"}))
    assert node.fsm.state is State.IDLE


def test_goal_pose_encodes_position_and_yaw(node):
    target = TargetPose("can", "t", x_m=2.0, y_m=3.0, yaw_rad=math.pi / 2)
    pose = node.goal_pose(target)
    assert pose.header.frame_id == "map"
    assert pose.pose.position.x == pytest.approx(2.0)
    assert pose.pose.position.y == pytest.approx(3.0)
    assert pose.pose.orientation.z == pytest.approx(math.sin(math.pi / 4))
    assert pose.pose.orientation.w == pytest.approx(math.cos(math.pi / 4))
