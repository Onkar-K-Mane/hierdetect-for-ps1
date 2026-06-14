import subprocess
import sys

def test_cli_help():
    """Ensure the CLI entry point is correctly installed and outputs the help menu."""
    result = subprocess.run([sys.executable, "-m", "hierdetect.cli", "--help"], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert "Hierarchical PowerShell" in result.stdout
    assert "--model-dir" in result.stdout

def test_cli_missing_args():
    """Ensure the CLI strictly requires the --model-dir argument."""
    result = subprocess.run([sys.executable, "-m", "hierdetect.cli", "--check"], capture_output=True, text=True)
    
    assert result.returncode != 0
    assert "the following arguments are required: --model-dir" in result.stderr