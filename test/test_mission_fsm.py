#!/usr/bin/env python3
# test_mission_fsm.py — TF35 T03: pure mission FSM transitions + emitted commands
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import pytest

from dome_mission.mission_fsm import (
    Command,
    CommandType,
    Intent,
    MissionFsm,
    Outcome,
    State,
)


@pytest.fixture
def fsm():
    return MissionFsm()


# --- explore behavior ---------------------------------------------------------

def test_explore_start_from_idle(fsm):
    cmds = fsm.on_intent(Intent.EXPLORE_START, map_name="lab")
    assert fsm.state is State.EXPLORING
    assert cmds == [Command(CommandType.START_EXPLORE, map_name="lab")]


def test_explore_done_returns_idle(fsm):
    fsm.on_intent(Intent.EXPLORE_START)
    cmds = fsm.on_done(Outcome.EXPLORED_DONE)
    assert fsm.state is State.IDLE
    assert cmds == []


def test_explore_no_targets_blocked_ends_behavior(fsm):
    fsm.on_intent(Intent.EXPLORE_START)
    fsm.on_done(Outcome.NO_TARGETS_BLOCKED)
    assert fsm.state is State.IDLE


def test_explore_stop_preempts(fsm):
    fsm.on_intent(Intent.EXPLORE_START)
    cmds = fsm.on_intent(Intent.EXPLORE_STOP)
    assert fsm.state is State.IDLE
    assert cmds == [Command(CommandType.CANCEL_EXPLORE)]


def test_explore_start_ignored_when_busy(fsm):
    fsm.on_intent(Intent.EXPLORE_START)
    cmds = fsm.on_intent(Intent.EXPLORE_START)
    assert fsm.state is State.EXPLORING
    assert cmds == []


# --- locate behavior (F33 Phase C) -------------------------------------------

def test_locate_start_drives_explore_primitive(fsm):
    cmds = fsm.on_intent(Intent.LOCATE_START, map_name="lab")
    assert fsm.state is State.LOCATING
    assert cmds == [Command(CommandType.START_EXPLORE, map_name="lab")]


def test_locate_stopped_returns_idle(fsm):
    fsm.on_intent(Intent.LOCATE_START)
    fsm.on_done(Outcome.STOPPED)
    assert fsm.state is State.IDLE


def test_locate_cancel_emits_cancel_explore(fsm):
    fsm.on_intent(Intent.LOCATE_START)
    cmds = fsm.on_intent(Intent.CANCEL)
    assert fsm.state is State.IDLE
    assert cmds == [Command(CommandType.CANCEL_EXPLORE)]


# --- go-to-target behavior ---------------------------------------------------

def test_go_to_target_from_idle(fsm):
    cmds = fsm.on_intent(Intent.GO_TO_TARGET, label="can")
    assert fsm.state is State.GOING_TO_TARGET
    assert cmds == [Command(CommandType.DRIVE_TO_TARGET, label="can")]


def test_arrived_returns_idle(fsm):
    fsm.on_intent(Intent.GO_TO_TARGET, label="can")
    cmds = fsm.on_done(Outcome.ARRIVED)
    assert fsm.state is State.IDLE
    assert cmds == []


def test_drive_failed_returns_idle(fsm):
    fsm.on_intent(Intent.GO_TO_TARGET, label="can")
    fsm.on_done(Outcome.DRIVE_FAILED)
    assert fsm.state is State.IDLE


def test_cancel_drive(fsm):
    fsm.on_intent(Intent.GO_TO_TARGET, label="can")
    cmds = fsm.on_intent(Intent.CANCEL)
    assert fsm.state is State.IDLE
    assert cmds == [Command(CommandType.CANCEL_DRIVE)]


def test_go_ignored_when_exploring(fsm):
    fsm.on_intent(Intent.EXPLORE_START)
    cmds = fsm.on_intent(Intent.GO_TO_TARGET, label="can")
    assert fsm.state is State.EXPLORING
    assert cmds == []


# --- defensive: stray events are no-ops --------------------------------------

def test_stop_when_idle_is_noop(fsm):
    cmds = fsm.on_intent(Intent.EXPLORE_STOP)
    assert fsm.state is State.IDLE
    assert cmds == []


def test_cancel_when_idle_is_noop(fsm):
    cmds = fsm.on_intent(Intent.CANCEL)
    assert fsm.state is State.IDLE
    assert cmds == []


def test_done_ignored_in_wrong_state(fsm):
    # A drive outcome while exploring must not end the explore behavior.
    fsm.on_intent(Intent.EXPLORE_START)
    fsm.on_done(Outcome.ARRIVED)
    assert fsm.state is State.EXPLORING


def test_full_intent_sequence(fsm):
    # explore -> done -> go -> arrive -> explore again
    assert fsm.on_intent(Intent.EXPLORE_START)[0].type is CommandType.START_EXPLORE
    fsm.on_done(Outcome.EXPLORED_DONE)
    assert fsm.on_intent(Intent.GO_TO_TARGET, label="door")[0].type is CommandType.DRIVE_TO_TARGET
    fsm.on_done(Outcome.ARRIVED)
    assert fsm.state is State.IDLE
    assert fsm.on_intent(Intent.EXPLORE_START)[0].type is CommandType.START_EXPLORE
    assert fsm.state is State.EXPLORING
