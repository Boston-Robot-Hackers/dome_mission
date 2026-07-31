#!/usr/bin/env python3
# intent_parser.py — pure /intent JSON -> mission Intent mapping
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

"""Pure `/intent` JSON -> mission Intent mapping (F35 / TF35 T04).

The `/intent` contract (std_msgs/String carrying a JSON object) is owned by
dome_mission after T04. This module is ROS-free so the mapping is unit-testable
without a graph; the node (mission_node) only deserializes the String and hands
the payload here.

Contract (name -> mission Intent):
  exploration_start  -> EXPLORE_START  (slots.map_name, optional; "" = session map)
  exploration_stop   -> EXPLORE_STOP
  navigation_go      -> GO_TO_TARGET   (slots.label)
  navigation_cancel  -> CANCEL

Unknown names / malformed JSON -> None (caller logs and drops).
"""

import json
from dataclasses import dataclass

from dome_mission.mission_fsm import Intent


@dataclass(frozen=True)
class ParsedIntent:
    intent: Intent
    label: str = ""
    map_name: str = ""


NAME_TO_INTENT = {
    "exploration_start": Intent.EXPLORE_START,
    "exploration_stop": Intent.EXPLORE_STOP,
    "navigation_go": Intent.GO_TO_TARGET,
    "navigation_cancel": Intent.CANCEL,
}


def parse_intent(json_str: str) -> ParsedIntent | None:
    """Map a raw `/intent` JSON payload to a `ParsedIntent`, or None if the
    JSON is malformed, not an object, or carries an unknown `name`."""
    try:
        payload = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None

    intent = NAME_TO_INTENT.get(payload.get("name", ""))
    if intent is None:
        return None

    slots = payload.get("slots") or {}
    if not isinstance(slots, dict):
        slots = {}
    label = slots.get("label", "") or ""
    map_name = slots.get("map_name", "") or ""
    return ParsedIntent(intent=intent, label=str(label), map_name=str(map_name))
