from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from quiz.tts import create_audio, speed_to_length_scale, split_by_punctuation, synthesize


class PunctuationTests(SimpleTestCase):
    def test_comma_has_shorter_pause_than_period(self):
        comma_chunks = split_by_punctuation("Hello, John.")
        period_chunks = split_by_punctuation("Hello. John.")

        self.assertEqual(comma_chunks[0], ("Hello,", 180))
        self.assertEqual(period_chunks[0], ("Hello.", 380))

    def test_ellipsis_has_dramatic_pause(self):
        self.assertEqual(
            split_by_punctuation("Hello... John.")[0],
            ("Hello...", 700),
        )

    def test_question_and_exclamation_are_kept_for_intonation(self):
        self.assertEqual(split_by_punctuation("Really?"), [("Really?", 420)])
        self.assertEqual(split_by_punctuation("Really!"), [("Really!", 320)])

    def test_hyphen_splits_words_without_being_spoken(self):
        self.assertEqual(
            split_by_punctuation("Wait-don't go."),
            [("Wait", 280), ("don't go.", 380)],
        )

    def test_colon_and_semicolon_split_clauses(self):
        self.assertEqual(
            split_by_punctuation("There are three things: food, water, and medicine."),
            [
                ("There are three things:", 300),
                ("food,", 180),
                ("water,", 180),
                ("and medicine.", 380),
            ],
        )
        self.assertEqual(
            split_by_punctuation("Well; I'm not sure."),
            [("Well;", 320), ("I'm not sure.", 380)],
        )


class VoiceSpeedTests(SimpleTestCase):
    def test_speed_is_converted_to_inverse_length_scale(self):
        self.assertEqual(speed_to_length_scale(1.0), 1.0)
        self.assertEqual(speed_to_length_scale(1.10), 0.9091)
        self.assertEqual(speed_to_length_scale(0.8), 1.25)

    def test_non_positive_speed_is_rejected(self):
        with self.assertRaisesMessage(ValueError, "lebih besar dari 0"):
            speed_to_length_scale(0)

    @patch("quiz.tts.subprocess.run")
    def test_synthesize_passes_length_scale_to_piper(self, run):
        run.return_value.returncode = 0

        synthesize("WOMAN", "Hello.", Path("voice.wav"), Decimal("1.10"))

        command = run.call_args.args[0]
        scale_index = command.index("--length-scale") + 1
        self.assertEqual(command[scale_index], "0.9091")

    @patch("quiz.tts.combine")
    @patch("quiz.tts.synthesize")
    def test_conversation_speeds_are_applied_per_actor(self, synthesize_mock, _combine):
        speeds = {"MAN": Decimal("0.90"), "WOMAN": Decimal("1.20")}
        models = {
            "MAN": "en_US-hfc_male-medium",
            "WOMAN": "en_US-hfc_female-medium",
        }

        create_audio("Man: Hello\nWoman: Hi", Path("conversation.wav"), speeds, models)

        self.assertEqual(synthesize_mock.call_args_list[0].args[3], Decimal("0.90"))
        self.assertEqual(synthesize_mock.call_args_list[1].args[3], Decimal("1.20"))
        self.assertEqual(synthesize_mock.call_args_list[0].args[4], "en_US-hfc_male-medium")
        self.assertEqual(synthesize_mock.call_args_list[1].args[4], "en_US-hfc_female-medium")

    @patch("quiz.tts.subprocess.run")
    def test_selected_voice_model_is_passed_to_piper(self, run):
        run.return_value.returncode = 0

        synthesize(
            "MAN",
            "Hello.",
            Path("voice.wav"),
            Decimal("1.00"),
            "en_US-hfc_male-medium",
        )

        command = run.call_args.args[0]
        model_index = command.index("--model") + 1
        self.assertTrue(command[model_index].endswith("en_US-hfc_male-medium.onnx"))

    def test_voice_model_must_match_actor_gender(self):
        with self.assertRaisesMessage(ValueError, "tidak valid"):
            synthesize(
                "MAN",
                "Hello.",
                Path("voice.wav"),
                Decimal("1.00"),
                "en_US-amy-medium",
            )
