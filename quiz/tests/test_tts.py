from django.test import SimpleTestCase

from quiz.tts import split_by_punctuation


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
