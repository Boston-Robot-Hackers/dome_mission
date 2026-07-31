#!/usr/bin/env python3
# mission_fsm.py — pure ROS-free mission-sequencing FSM
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Pure, ROS-free mission-sequencing FSM (F35 / TF35 T03).

Maps intent events and behavior-completion outcomes to state transitions and
emitted primitive commands. The ROS layer (mission_node) executes those commands
against the dome_nav ExploreArea action and Nav2 NavigateToPose; this module
knows nothing about ROS, actions, or label->pose resolution (dome_mission T05).

Behaviors:
  - explore:        IDLE -> EXPLORING -> IDLE (done on no-frontiers / stop)
  - locate targets: IDLE -> LOCATING -> IDLE (explore while semantic ingest
                    runs; F33 Phase C — ingest is always-on and external, so
                    LOCATING drives the same explore primitive, differing only
                    in mission intent/telemetry)
  - go to target:   IDLE -> GOING_TO_TARGET -> IDLE (drive to a resolved target)

Boundary decision (F35 open q, settled 2026-07-31): per-goal stop/abort
authority (goal timeouts, STUCK_T_S, blacklist exhaustion, per-goal
reselection) stays DOWN in dome_nav's explorer watchdog and never surfaces as
an FSM event. The FSM owns only mission-level authority: start/stop/preempt
intents and the single terminal ExploreArea outcome (EXPLORED_DONE / STOPPED /
NO_TARGETS_BLOCKED).
"""

from dataclasses import dataclass, field
from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    EXPLORING = auto()
    LOCATING = auto()
    GOING_TO_TARGET = auto()


class Intent(Enum):
    EXPLORE_START = auto()
    EXPLORE_STOP = auto()
    LOCATE_START = auto()
    GO_TO_TARGET = auto()
    CANCEL = auto()


class Outcome(Enum):
    """Terminal behavior results. Explore outcomes mirror the ExploreArea action
    result; drive outcomes summarize a NavigateToPose result."""

    EXPLORED_DONE = auto()
    STOPPED = auto()
    NO_TARGETS_BLOCKED = auto()
    ARRIVED = auto()
    DRIVE_FAILED = auto()


class CommandType(Enum):
    START_EXPLORE = auto()
    CANCEL_EXPLORE = auto()
    DRIVE_TO_TARGET = auto()
    CANCEL_DRIVE = auto()


@dataclass(frozen=True)
class Command:
    """A primitive for the ROS layer to execute. label/map_name carry the
    payload the executor needs; label->pose resolution happens downstream."""

    type: CommandType
    map_name: str = ""
    label: str = ""


EXPLORE_STATES = (State.EXPLORING, State.LOCATING)
EXPLORE_OUTCOMES = (Outcome.EXPLORED_DONE, Outcome.STOPPED, Outcome.NO_TARGETS_BLOCKED)
DRIVE_OUTCOMES = (Outcome.ARRIVED, Outcome.DRIVE_FAILED)


@dataclass
class MissionFsm:
    """Deterministic mission FSM. on_intent/on_done return the commands to emit
    and mutate state; both ignore events that don't apply to the current state
    (return [], state unchanged) so a stray event never wedges the FSM."""

    state: State = field(default=State.IDLE)

    def on_intent(
        self, intent: Intent, *, label: str = "", map_name: str = ""
    ) -> list[Command]:
        if intent in (Intent.EXPLORE_START, Intent.LOCATE_START):
            return self.begin_explore(intent, map_name)
        if intent is Intent.GO_TO_TARGET:
            return self.begin_drive(label)
        if intent in (Intent.EXPLORE_STOP, Intent.CANCEL):
            return self.abort(intent)
        return []

    def begin_explore(self, intent: Intent, map_name: str) -> list[Command]:
        if self.state is not State.IDLE:
            return []
        starting = intent is Intent.EXPLORE_START
        self.state = State.EXPLORING if starting else State.LOCATING
        return [Command(CommandType.START_EXPLORE, map_name=map_name)]

    def begin_drive(self, label: str) -> list[Command]:
        # IDLE-only for now; concurrent preempt (go while exploring) waits on
        # T05 label->pose + a preempt policy.
        if self.state is not State.IDLE:
            return []
        self.state = State.GOING_TO_TARGET
        return [Command(CommandType.DRIVE_TO_TARGET, label=label)]

    def abort(self, intent: Intent) -> list[Command]:
        if self.state in EXPLORE_STATES:
            self.state = State.IDLE
            return [Command(CommandType.CANCEL_EXPLORE)]
        if intent is Intent.CANCEL and self.state is State.GOING_TO_TARGET:
            self.state = State.IDLE
            return [Command(CommandType.CANCEL_DRIVE)]
        return []

    def on_done(self, outcome: Outcome) -> list[Command]:
        """A running behavior reported a terminal outcome; return to IDLE. No
        follow-up command — the executor already saw the action result."""
        explore_done = self.state in EXPLORE_STATES and outcome in EXPLORE_OUTCOMES
        drive_done = self.state is State.GOING_TO_TARGET and outcome in DRIVE_OUTCOMES
        if explore_done or drive_done:
            self.state = State.IDLE
        return []
