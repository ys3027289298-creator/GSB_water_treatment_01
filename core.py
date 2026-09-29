"""水处理厂核心逻辑：水样、药剂、滤膜和出水。"""

import json


FIXED_DATE = "2026-09-29"
MAX_CHEMICAL = 100
MAX_TREAT_VOLUME = 100
SUPPLY_QUALITY_LIMIT = 60


def new_game():
    return {
        "samples": {},
        "chemical": 50,
        "quality": 80,
        "batch_id": 0,
        "date": FIXED_DATE,
        "volume": 0,
        "membrane_fault": False,
        "pressure": 100,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    defaults = new_game()
    for key, value in defaults.items():
        state.setdefault(key, value)
    return state


def test_sample(state, sample_id):
    if not sample_id:
        return False
    if sample_id in state["samples"]:
        return False
    state["samples"][sample_id] = True
    return True


def supply(state):
    if state.get("quality", 0) < SUPPLY_QUALITY_LIMIT:
        return False
    return True


def volume(state):
    amount = state.get("volume", 0)
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return 0
    if amount < 0:
        return 0
    return min(amount, MAX_TREAT_VOLUME)


def treat(state, amount):
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if amount <= 0:
        return False
    if state.get("chemical", 0) < amount:
        return False
    state["chemical"] -= amount
    state["volume"] = min(state.get("volume", 0) + amount, MAX_TREAT_VOLUME)
    return True


def cancel_treat(state, amount):
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return False
    if amount <= 0:
        return False
    chemical = state.get("chemical", 0) + amount
    state["chemical"] = min(chemical, MAX_CHEMICAL)
    state["volume"] = max(0, state.get("volume", 0) - amount)
    return True


def output(state):
    if state.get("membrane_fault"):
        return False
    if volume(state) <= 0:
        return False
    return True


def pollute(state):
    state["quality"] -= 10
    if state["quality"] < 0:
        state["quality"] = 0
    return state["quality"]


def pressurize(state):
    if state.get("pressure", 0) <= 0:
        return False
    return True


COMMANDS = ("test", "supply", "volume", "cancel", "output",
            "pollute", "pressurize", "save", "load", "quit")


def dispatch(state, line):
    parts = line.split()
    command = parts[0]
    if command not in COMMANDS:
        return "非法命令"
    if command == "test":
        if len(parts) != 2:
            return "非法命令"
        return "ok" if test_sample(state, parts[1]) else "重复水样"
    if command == "supply":
        return "ok" if supply(state) else "水质超标，禁止供水"
    if command == "volume":
        return str(volume(state))
    if command == "cancel":
        if len(parts) != 2:
            return "非法命令"
        return "ok" if cancel_treat(state, parts[1]) else "取消失败"
    if command == "output":
        return "ok" if output(state) else "滤膜故障或无出水"
    if command == "pollute":
        return str(pollute(state))
    if command == "pressurize":
        return "ok" if pressurize(state) else "压力不足"
    if command == "save":
        return save_state(state)
    if command == "load":
        return "非法命令" if len(parts) != 2 else save_state(load_state(parts[1]))
    return ""


def main():
    print("水处理厂 - 命令: test/supply/volume/cancel/output/pollute/pressurize/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        print(dispatch(state, raw))


if __name__ == "__main__":
    main()
