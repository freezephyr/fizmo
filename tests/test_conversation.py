from __future__ import annotations

import unittest

from fizmo.hardware.mock import MockMicrophone
from fizmo.runtime import build_mock_runtime


class ConversationTests(unittest.TestCase):
    def test_silent_conversation_turn(self) -> None:
        runtime = build_mock_runtime()

        turn = runtime.conversation.run_once(duration_s=0.1)

        self.assertEqual(turn.transcription.text, "")
        self.assertEqual(turn.response.text, "I did not hear anything.")

    def test_heard_conversation_turn(self) -> None:
        runtime = build_mock_runtime()
        self.assertIsInstance(runtime.conversation.microphone, MockMicrophone)
        runtime.conversation.microphone.rms = 0.02

        turn = runtime.conversation.run_once(duration_s=0.1)

        self.assertEqual(turn.transcription.text, "hello fizmo")
        self.assertEqual(turn.response.text, "I heard: hello fizmo")


if __name__ == "__main__":
    unittest.main()
