#!/usr/bin/env python3
# test_label_resolver.py — TF35 T05: pure label->pose resolution + nearest match
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import math

import pytest

from dome_mission.label_resolver import (
    SemanticTargetStore,
    TargetPose,
    yaw_from_quaternion,
)


def target(label, x_m, y_m, target_id="t"):
    return TargetPose(label=label, target_id=target_id, x_m=x_m, y_m=y_m, yaw_rad=0.0)


@pytest.fixture
def store():
    return SemanticTargetStore()


def test_resolve_no_match(store):
    store.update([target("can", 1.0, 1.0)])
    assert store.resolve("cup", (0.0, 0.0)) is None


def test_resolve_empty_store(store):
    assert store.resolve("can", (0.0, 0.0)) is None


def test_resolve_single_match(store):
    can = target("can", 2.0, 3.0)
    store.update([can])
    assert store.resolve("can", (0.0, 0.0)) == can


def test_resolve_returns_nearest(store):
    near = target("can", 1.0, 0.0, target_id="near")
    far = target("can", 9.0, 0.0, target_id="far")
    store.update([far, near])
    assert store.resolve("can", (0.0, 0.0)).target_id == "near"


def test_resolve_nearest_from_non_origin(store):
    a = target("box", 0.0, 0.0, target_id="a")
    b = target("box", 10.0, 10.0, target_id="b")
    store.update([a, b])
    assert store.resolve("box", (9.0, 9.0)).target_id == "b"


def test_resolve_no_robot_pose_returns_first(store):
    first = target("cup", 5.0, 5.0, target_id="first")
    second = target("cup", 0.1, 0.1, target_id="second")
    store.update([first, second])
    assert store.resolve("cup", None).target_id == "first"


def test_yaw_from_quaternion_identity():
    assert yaw_from_quaternion(0.0, 1.0) == pytest.approx(0.0)


def test_yaw_from_quaternion_ninety_deg():
    z = math.sin(math.pi / 4)
    w = math.cos(math.pi / 4)
    assert yaw_from_quaternion(z, w) == pytest.approx(math.pi / 2)
