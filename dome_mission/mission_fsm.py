"""Pure, ROS-free mission-sequencing FSM (F35 / TF35 T03).

Drives three behaviors by mapping intent events and behavior-completion
outcomes to state transitions and emitted *primitive commands*. The ROS layer
(mission_node, later tasks) executes those commands against the dome_nav
`ExploreArea` action and Nav2 `NavigateToPose`; this module knows nothing about
ROS, actions, or label->pose resolution (that is dome_mission T05).

Behaviors:
  - explore:        IDLE -> EXPLORING -> IDLE (done on no-frontiers / stop)
  - locate targets: IDLE -> LOCATING -> IDLE (explore while semantic ingest
                    runs; F33 Phase C — the ingest pipeline is always-on and
                    external to the FSM, so LOCATING drives the same explore
                    primitive and differs only in mission intent/telemetry)
  - go to target:   IDLE -> GOING_TO_TARGET -> IDLE (drive to a resolved target)

Boundary decision (F35 open q, settled here 2026-07-31):
  Per-goal stop/abort authority stays DOWN in dome_nav's explorer watchdog —
  goal timeouts, STUCK_T_S, blacklist exhaustion, per-goal reselection are the
  explorer's job and never surface as FSM events. The FSM owns only
  MISSION-level authority: start/stop/preempt intents and the single terminal
  outcome the ExploreArea action reports (EXPLORED_DONE / STOPPED /
  NO_TARGETS_BLOCKED). The watchdog's internal recovery is invisible here; only
  its final give-up (NO_TARGETS_BLOCKED) ends the behavior.
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
    """Terminal behavior results. Explore outcomes mirror the ExploreArea
    action result; drive outcomes summarize a NavigateToPose result."""

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
    """A primitive the ROS layer must execute. `label`/`map_name` carry the
    payload the executor needs; label->pose resolution happens downstream."""

    type: CommandType
    map_name: str = ""
    label: str = ""


_EXPLORE_STATES = (State.EXPLORING, State.LOCATING)


@dataclass
class MissionFsm:
    """Deterministic mission FSM. `on_intent`/`on_done` return the commands to
    emit and mutate `state`; both ignore events that don't apply to the current
    state (return `[]`, state unchanged) so a stray event never wedges the FSM.
    """

    state: State = field(default=State.IDLE)

    def on_intent(self, intent: Intent, *, label: str = "", map_name: str = "") -> list[Command]:
        if intent is Intent.EXPLORE_START:
            if self.state is State.IDLE:
                self.state = State.EXPLORING
                return [Command(CommandType.START_EXPLORE, map_name=map_name)]
            return []

        if intent is Intent.LOCATE_START:
            if self.state is State.IDLE:
                self.state = State.LOCATING
                return [Command(CommandType.START_EXPLORE, map_name=map_name)]
            return []

        if intent is Intent.EXPLORE_STOP:
            if self.state in _EXPLORE_STATES:
                self.state = State.IDLE
                return [Command(CommandType.CANCEL_EXPLORE)]
            return []

        if intent is Intent.GO_TO_TARGET:
            # IDLE-only for now; concurrent preempt (go while exploring) is a
            # future extension once T05 lands label->pose + preempt policy.
            if self.state is State.IDLE:
                self.state = State.GOING_TO_TARGET
                return [Command(CommandType.DRIVE_TO_TARGET, label=label)]
            return []

        if intent is Intent.CANCEL:
            if self.state in _EXPLORE_STATES:
                self.state = State.IDLE
                return [Command(CommandType.CANCEL_EXPLORE)]
            if self.state is State.GOING_TO_TARGET:
                self.state = State.IDLE
                return [Command(CommandType.CANCEL_DRIVE)]
            return []

        return []

    def on_done(self, outcome: Outcome) -> list[Command]:
        """A running behavior reported a terminal outcome. Returns to IDLE; no
        follow-up command (the executor already saw the action result)."""
        explore_outcomes = (
            Outcome.EXPLORED_DONE,
            Outcome.STOPPED,
            Outcome.NO_TARGETS_BLOCKED,
        )
        drive_outcomes = (Outcome.ARRIVED, Outcome.DRIVE_FAILED)

        if self.state in _EXPLORE_STATES and outcome in explore_outcomes:
            self.state = State.IDLE
        elif self.state is State.GOING_TO_TARGET and outcome in drive_outcomes:
            self.state = State.IDLE
        return []
