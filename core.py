"""水处理厂核心逻辑：水样、药剂、滤膜和出水。

系统按批次处理水样、药剂、滤膜和出水。状态以 JSON 存档，演示使用固定日期。
"""

import json

FIXED_DATE = "2026-09-29"
INITIAL_CHEMICAL = 50
INITIAL_QUALITY = 80
SUPPLY_QUALITY_MIN = 60
POOL_CAPACITY = 100
POLLUTE_PENALTY = 10
INITIAL_PRESSURE = 10


def new_game():
    return {
        "date": FIXED_DATE,
        "samples": {},
        "chemical": INITIAL_CHEMICAL,
        "quality": INITIAL_QUALITY,
        "volume": 0,
        "output": 0,
        "pressure": INITIAL_PRESSURE,
        "membrane_fault": False,
        "polluted_batch_id": None,
        "batch_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    required = (
        "samples",
        "chemical",
        "quality",
        "volume",
        "output",
        "pressure",
        "membrane_fault",
        "polluted_batch_id",
        "batch_id",
    )
    missing = [key for key in required if key not in state]
    if missing:
        raise ValueError("存档数据不完整: " + ", ".join(missing))
    if not isinstance(state["samples"], dict):
        raise ValueError("水样数据格式错误")
    return state


def test_sample(state, sample_id):
    if not isinstance(sample_id, str) or not sample_id:
        raise ValueError("水样编号不能为空")
    if sample_id in state["samples"]:
        return False
    state["samples"][sample_id] = {
        "batch_id": state["batch_id"],
        "date": state.get("date", FIXED_DATE),
    }
    return True


def supply(state):
    if state["quality"] < SUPPLY_QUALITY_MIN:
        return False
    if state.get("membrane_fault", False):
        return False
    return True


def volume(state):
    current = state.get("volume", 0)
    if current < 0:
        return 0
    if current > POOL_CAPACITY:
        return POOL_CAPACITY
    return current


def cancel_treat(state, amount):
    if amount < 0:
        raise ValueError("取消处理量不能为负")
    state["chemical"] += amount
    return True


def output(state):
    if state.get("membrane_fault", False):
        return False
    produced = volume(state)
    state["output"] = state.get("output", 0) + produced
    return True


def pollute(state):
    if state.get("polluted_batch_id") == state["batch_id"]:
        return state["quality"]
    state["quality"] -= POLLUTE_PENALTY
    if state["quality"] < 0:
        state["quality"] = 0
    state["polluted_batch_id"] = state["batch_id"]
    return state["quality"]


def pressurize(state):
    if state.get("pressure", 0) <= 0:
        return False
    state["pressure"] -= 1
    return True


class CommandError(Exception):
    pass


def _parse_amount(text, name):
    try:
        value = int(text)
    except (TypeError, ValueError):
        raise CommandError(name + " 必须是非负整数")
    if value < 0:
        raise CommandError(name + " 不能为负")
    return value


def run_command(state, raw):
    parts = raw.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "test":
        if len(args) != 1:
            raise CommandError("用法: test <水样编号>")
        if test_sample(state, args[0]):
            return "已检测水样 " + args[0]
        return "水样重复: " + args[0]

    if cmd == "supply":
        if supply(state):
            return "允许供水"
        return "水质超标或滤膜故障，停止供水"

    if cmd == "volume":
        if len(args) == 0:
            return "当前处理量: " + str(volume(state))
        if len(args) > 1:
            raise CommandError("用法: volume [处理量]")
        value = _parse_amount(args[0], "处理量")
        if value > POOL_CAPACITY:
            return "超过池容量上限 " + str(POOL_CAPACITY)
        state["volume"] = value
        return "处理量设为 " + str(value)

    if cmd == "cancel":
        if len(args) != 1:
            raise CommandError("用法: cancel <药剂量>")
        amount = _parse_amount(args[0], "药剂量")
        cancel_treat(state, amount)
        return "已取消处理，返还药剂 " + str(amount)

    if cmd == "output":
        if output(state):
            return "出水已计入"
        return "滤膜故障，无法出水"

    if cmd == "pollute":
        return "水质: " + str(pollute(state))

    if cmd == "pressurize":
        if pressurize(state):
            return "加压成功"
        return "压力不足，无法加压"

    if cmd == "save":
        return save_state(state)

    if cmd == "date":
        return state.get("date", FIXED_DATE)

    raise CommandError("非法命令: " + cmd)


def main():
    state = new_game()
    print("水处理厂 日期:" + FIXED_DATE)
    print("命令: test/supply/volume/cancel/output/pollute/pressurize/save/date/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        try:
            print(run_command(state, raw))
        except CommandError as exc:
            print("错误: " + str(exc))


if __name__ == "__main__":
    main()
