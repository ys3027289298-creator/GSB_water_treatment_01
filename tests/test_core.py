import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_sample(self):
        state = core.new_game()
        self.assertTrue(core.test_sample(state, "S1"))
        self.assertFalse(core.test_sample(state, "S1"))

    def test_02_no_supply_when_bad_quality(self):
        state = core.new_game()
        state["quality"] = 10
        result = core.supply(state)
        self.assertFalse(result)

    def test_03_volume_by_capacity(self):
        state = core.new_game()
        state["volume"] = 60
        self.assertEqual(core.volume(state), 60)

    def test_04_cancel_treat_refunds(self):
        state = core.new_game()
        state["chemical"] = 40
        core.cancel_treat(state, 10)
        self.assertEqual(state["chemical"], 50)

    def test_05_no_output_on_fault(self):
        state = core.new_game()
        state["membrane_fault"] = True
        result = core.output(state)
        self.assertFalse(result)

    def test_06_pollute_once(self):
        state = core.new_game()
        core.pollute(state)
        self.assertEqual(state["quality"], 70)

    def test_07_no_pressurize_without_pressure(self):
        state = core.new_game()
        state["pressure"] = 0
        result = core.pressurize(state)
        self.assertFalse(result)

    def test_08_load_preserves_batch(self):
        state = core.new_game()
        state["batch_id"] = 5
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["batch_id"], 5)


if __name__ == "__main__":
    unittest.main()
