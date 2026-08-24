import unittest

from description_assembler import assemble_description


class AssembleDescriptionTest(unittest.TestCase):
    def test_appends_summary_after_template_separated_by_blank_line(self):
        result = assemble_description("既有樣板內容", "雙語簡介文字")

        self.assertEqual(result, "既有樣板內容\n\n雙語簡介文字")

    def test_returns_template_unchanged_when_summary_is_empty_or_none(self):
        self.assertEqual(assemble_description("既有樣板內容", ""), "既有樣板內容")
        self.assertEqual(assemble_description("既有樣板內容", None), "既有樣板內容")

    def test_truncates_summary_to_respect_char_limit_without_touching_template(self):
        template = "T" * 100
        summary = "S" * 50

        result = assemble_description(template, summary, char_limit=120)

        self.assertTrue(result.startswith(template + "\n\n"))
        self.assertEqual(len(result), 120)
        self.assertEqual(result, template + "\n\n" + "S" * 18)

    def test_truncates_template_itself_when_it_alone_exceeds_the_limit(self):
        template = "T" * 200

        result = assemble_description(template, "任何簡介", char_limit=120)

        self.assertEqual(result, template[:120])
        self.assertEqual(len(result), 120)


if __name__ == "__main__":
    unittest.main()
