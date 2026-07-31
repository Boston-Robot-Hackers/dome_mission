#!/usr/bin/env python3
# test_mission_node.py — TF35 T04: /intent payloads drive the node's FSM
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import json

import pytest
import rclpy
from std_msgs.msg import String

from dome_mission.mission_fsm import State
from dome_mission.mission_node import MissionNode


@pytest.fixture(scope="module", autouse=True)
def ros():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    n = MissionNode()
    yield n
    n.destroy_node()


def _msg(name, slots=None):
    m = String()
    m.data = json.dumps({"name": name, "source": "cli", "slots": slots or {}})
    return m


def test_intent_subscription_exists(node):
    # Exactly one /intent handler lives here (single-handler invariant, T04).
    assert node.intent_sub.topic_name == "/intent"


def test_exploration_start_drives_fsm(node):
    node.on_intent(_msg("exploration_start"))
    assert node.fsm.state is State.EXPLORING


def test_stop_returns_idle(node):
    node.on_intent(_msg("exploration_start"))
    node.on_intent(_msg("exploration_stop"))
    assert node.fsm.state is State.IDLE


def test_navigation_go_drives_to_target(node):
    node.on_intent(_msg("navigation_go", {"label": "can"}))
    assert node.fsm.state is State.GOING_TO_TARGET


def test_cancel_returns_idle(node):
    node.on_intent(_msg("navigation_go", {"label": "can"}))
    node.on_intent(_msg("navigation_cancel"))
    assert node.fsm.state is State.IDLE


def test_malformed_intent_is_ignored(node):
    bad = String()
    bad.data = "{not json"
    node.on_intent(bad)
    assert node.fsm.state is State.IDLE
