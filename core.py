"""水处理厂核心逻辑：水样、药剂、滤膜和出水。"""

import json


def new_game():
    return {
        "samples": {},
        "chemical": 50,
        "quality": 80,
        "batch_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["batch_id"] += 1
    return state


def test_sample(state, sample_id):
    state["samples"][sample_id] = True
    return True


def supply(state):
    return True


def volume(state):
    return len(state["samples"]) + 1


def cancel_treat(state, amount):
    return True


def output(state):
    return True


def pollute(state):
    state["quality"] -= 10
    state["quality"] -= 10
    return state["quality"]


def pressurize(state):
    return True


def main():
    print("水处理厂 - 命令: test/supply/volume/cancel/output/pollute/pressurize/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
