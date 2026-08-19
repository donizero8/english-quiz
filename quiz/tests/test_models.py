from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from quiz.models import Conversation


class ConversationVoiceSpeedTests(TestCase):
    def test_default_voice_speeds(self):
        conversation = Conversation(title="Example", slug="example", script="Man: Hello")

        self.assertEqual(conversation.man_speed, Decimal("1.00"))
        self.assertEqual(conversation.woman_speed, Decimal("1.10"))
        self.assertEqual(conversation.man_voice, "en_US-ryan-medium")
        self.assertEqual(conversation.woman_voice, "en_US-amy-medium")

    def test_voice_speed_must_be_within_supported_range(self):
        conversation = Conversation(
            title="Invalid",
            slug="invalid",
            script="Woman: Hello",
            man_speed=Decimal("0.74"),
            woman_speed=Decimal("1.41"),
        )

        with self.assertRaises(ValidationError) as error:
            conversation.full_clean()

        self.assertIn("man_speed", error.exception.message_dict)
        self.assertIn("woman_speed", error.exception.message_dict)

    def test_voice_must_be_available_for_actor_gender(self):
        conversation = Conversation(
            title="Wrong voice",
            slug="wrong-voice",
            script="Man: Hello",
            man_voice="en_US-amy-medium",
        )

        with self.assertRaises(ValidationError) as error:
            conversation.full_clean()

        self.assertIn("man_voice", error.exception.message_dict)
