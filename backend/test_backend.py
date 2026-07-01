import os
import unittest
import tempfile
from parser import DocumentParser
from detector import AIContentDetector

class TestAIContentDetectorBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=== Initializing AI Content Detector for Tests ===")
        # Load the detector once
        cls.detector = AIContentDetector()
        cls.parser = DocumentParser()

    def test_parser_txt(self):
        print("\n--- Testing Parser on TXT file ---")
        sample_text = (
            "Paragraph one is here. It has some text.\n\n"
            "Paragraph two is here. It is separated by a blank line."
        )
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_file.write(sample_text)
            temp_file_path = temp_file.name

        try:
            parsed = self.parser.parse_file(temp_file_path)
            self.assertEqual(len(parsed["paragraphs"]), 2)
            self.assertIn("Paragraph one", parsed["text"])
            self.assertEqual(parsed["paragraphs"][0], "Paragraph one is here. It has some text.")
            self.assertEqual(parsed["paragraphs"][1], "Paragraph two is here. It is separated by a blank line.")
            print("Parser TXT test PASSED")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def test_detector_ai_vs_human(self):
        print("\n--- Testing Detector AI vs Human scoring ---")
        
        # Highly repetitive, standard transition word structured text (AI-like)
        ai_text = (
            "The artificial intelligence model is very good. The artificial intelligence model can write text. "
            "The artificial intelligence model is trained on a lot of data. It is important to note that the "
            "artificial intelligence model can generate text very fast. It is crucial to outline that the "
            "artificial intelligence model is very useful. Therefore, the artificial intelligence model "
            "will change the world."
        )
        
        # High sentence variation, informal, lower vocabulary overlap (Human-like)
        human_text = (
            "Wait. What just happened? I cannot believe that this project is finally compiling after so "
            "many hours of debugging and dealing with weird environment issues on my local machine. "
            "It feels absolutely amazing! But just a few minutes ago, I was completely ready to give up "
            "and choose a different career path. Programming is a wild ride."
        )

        ai_analysis = self.detector.analyze_paragraph(ai_text)
        human_analysis = self.detector.analyze_paragraph(human_text)

        print(f"AI Sample Score: {ai_analysis['ai_score']}% (Flag: {ai_analysis['flag']}, Perplexity Score: {ai_analysis['perplexity_score']})")
        print(f"Human Sample Score: {human_analysis['ai_score']}% (Flag: {human_analysis['flag']}, Perplexity Score: {human_analysis['perplexity_score']})")

        # The AI score for the AI text should be significantly higher than the Human text
        self.assertGreater(ai_analysis["ai_score"], human_analysis["ai_score"])
        self.assertLess(human_analysis["ai_score"], 45)  # Human score should be low/medium
        self.assertGreater(ai_analysis["ai_score"], 50)  # AI score should be high/very high
        print("AI vs Human classification test PASSED")

    def test_empty_document(self):
        print("\n--- Testing Empty Paragraph Handling ---")
        analysis = self.detector.analyze_paragraph("")
        self.assertEqual(analysis["ai_score"], 0.0)
        self.assertEqual(analysis["flag"], "Very Low")
        print("Empty paragraph test PASSED")

if __name__ == "__main__":
    unittest.main()
