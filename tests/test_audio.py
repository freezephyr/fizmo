from __future__ import annotations

import unittest

from fizmo.config import load_robot_config
from fizmo.runtime import build_mock_runtime


class AudioConfigTests(unittest.TestCase):
    def test_loads_configured_wake_word_and_audio(self) -> None:
        config = load_robot_config()

        self.assertEqual(config.agent.wake_word, "Fiz")
        self.assertEqual(config.audio.microphone_kind, "usb_alsa")
        self.assertEqual(config.audio.sample_rate_hz, 16000)
        self.assertEqual(config.audio.channels, 1)

    def test_mock_runtime_can_listen(self) -> None:
        runtime = build_mock_runtime()

        result = runtime.interaction.listen(duration_s=0.1)

        self.assertTrue(result.ok)
        self.assertEqual(result.tool, "listen")
        self.assertEqual(result.status, "silence")
        self.assertEqual(result.data["sample_rate_hz"], 16000)


if __name__ == "__main__":
    unittest.main()
