import unittest
import re
from unittest.mock import MagicMock
from workers.translation_worker import TranslationWorker

class TestTextCleaning(unittest.TestCase):
    def setUp(self):
        # Mock dependencies for TranslationWorker
        self.state = MagicMock()
        self.capture = MagicMock()
        self.ocr = MagicMock()
        self.translator = MagicMock()
        self.worker = TranslationWorker(self.state, self.capture, self.ocr, self.translator)

    def test_normalize_ellipses(self):
        self.assertEqual(self.worker._clean_text("Wait for it...."), "Wait for it...")
        self.assertEqual(self.worker._clean_text("Wait for it.........."), "Wait for it...")

    def test_remove_garbage(self):
        self.assertEqual(self.worker._clean_text("Hello #$@ World!"), "Hello #$@ World!")
        self.assertEqual(self.worker._clean_text("Price: 100€"), "Price: 100") # € still removed as it's non-ASCII and not in whitelist

    def test_collapse_spaces(self):
        self.assertEqual(self.worker._clean_text("  Too   many    spaces  "), "Too many spaces")

    def test_empty_input(self):
        self.assertEqual(self.worker._clean_text(""), "")
        self.assertEqual(self.worker._clean_text(None), "")

    def test_full_cleaning(self):
        input_text = "  Strange... symbols @#$% and    too many dots....  "
        expected = "Strange... symbols @#$% and too many dots..."
        self.assertEqual(self.worker._clean_text(input_text), expected)

if __name__ == '__main__':
    unittest.main()
