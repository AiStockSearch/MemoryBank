import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import scripts.ai_assistant as ai

class TestAIAssistant(unittest.TestCase):
    @patch('requests.post')
    def test_create_snapshot_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"archive": "snapshot-test.zip"}
        archive = ai.create_snapshot()
        self.assertEqual(archive, "snapshot-test.zip")

    @patch('requests.post')
    def test_create_snapshot_error(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Error"
        archive = ai.create_snapshot()
        self.assertIsNone(archive)

    def test_generate_kp_template(self):
        bug = ai.generate_kp_template("bug", "test-bug")
        self.assertIn("bug-test-bug", bug)
        feature = ai.generate_kp_template("feature", "test-feature")
        self.assertIn("feature-test-feature", feature)
        epic = ai.generate_kp_template("epic", "test-epic")
        self.assertIn("epic-test-epic", epic)

    @patch("builtins.open", new_callable=mock_open)
    def test_create_knowledge_package(self, mock_file):
        ai.create_knowledge_package("test-kp", "# Test KP\n")
        mock_file.assert_called_with("memory-bank/knowledge_packages/test-kp.md", "w", encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open, read_data="[2024-06-21] [ERROR] Ошибка\n")
    @patch("scripts.ai_assistant.rollback_to_snapshot")
    @patch("scripts.ai_assistant.prompt_user", return_value=True)
    def test_analyze_audit_log_with_error(self, mock_prompt, mock_rollback, mock_file):
        # Эмулируем наличие ошибки в auditLog.md и согласие на откат
        ai.analyze_audit_log()
        mock_rollback.assert_called_once_with("snapshot-X")

if __name__ == "__main__":
    unittest.main() 