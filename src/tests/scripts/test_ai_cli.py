import subprocess
import pytest

@pytest.mark.parametrize(
    "args,expected_output,expected_code",
    [
        (["--help"], "Usage:", 0),
        (["generate-spec", "--type", "landing"], "Спецификация", 0),
        (["unknown-command"], "error", 1),
    ]
)
def test_ai_cli_command(args, expected_output, expected_code):
    """Тестирует CLI-команду ai_cli.py с разными аргументами."""
    result = subprocess.run(
        ["python3", "src/scripts/ai_cli.py"] + args,
        capture_output=True,
        text=True
    )
    assert expected_output in result.stdout or expected_output in result.stderr
    assert result.returncode == expected_code 