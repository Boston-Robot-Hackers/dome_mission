#!/usr/bin/env python3
# test_intent_parser.py — TF35 T04: pure /intent JSON -> mission Intent mapping
# Author: Pito Salas and Claude Code
# Open Source Under MIT license

import json

from dome_mission.intent_parser import ParsedIntent, parse_intent
from dome_mission.mission_fsm import Intent


def _payload(name, slots=None, source="cli"):
    return json.dumps({"name": name, "source": source, "slots": slots or {}})


def test_exploration_start():
    p = parse_intent(_payload("exploration_start"))
    assert p == ParsedIntent(Intent.EXPLORE_START)


def test_exploration_start_with_map_name():
    p = parse_intent(_payload("exploration_start", {"map_name": "lab"}))
    assert p == ParsedIntent(Intent.EXPLORE_START, map_name="lab")


def test_exploration_stop():
    assert parse_intent(_payload("exploration_stop")) == ParsedIntent(Intent.EXPLORE_STOP)


def test_navigation_go_carries_label():
    p = parse_intent(_payload("navigation_go", {"label": "can"}))
    assert p == ParsedIntent(Intent.GO_TO_TARGET, label="can")


def test_navigation_cancel():
    assert parse_intent(_payload("navigation_cancel")) == ParsedIntent(Intent.CANCEL)


def test_unknown_name_is_none():
    assert parse_intent(_payload("bogus_verb")) is None


def test_malformed_json_is_none():
    assert parse_intent("{not valid json") is None


def test_non_object_json_is_none():
    assert parse_intent("[1, 2, 3]") is None


def test_missing_slots_defaults_empty():
    p = parse_intent(json.dumps({"name": "navigation_go"}))
    assert p == ParsedIntent(Intent.GO_TO_TARGET, label="")


def test_non_dict_slots_ignored():
    p = parse_intent(json.dumps({"name": "navigation_go", "slots": "oops"}))
    assert p == ParsedIntent(Intent.GO_TO_TARGET, label="")
