import os
import sys

import pytest

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Disable auth for tests
os.environ["APP_PASSWORD_HASH"] = ""

# Test runner script

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "-s", "tests/test_territories_endpoint.py"]))
