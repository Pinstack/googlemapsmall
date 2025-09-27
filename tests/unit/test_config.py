"""Unit tests for configuration management.

Tests configuration loading, validation, and management functionality.
These tests MUST FAIL initially (no config.py implementation yet) - TDD approach.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest


class TestConfigurationLoading:
    """Test cases for configuration file loading."""

    def test_load_json_config_file(self) -> None:
        """Test loading configuration from JSON file."""
        # This test will fail until config.py is implemented
        from src.config import load_config

        config_data = {
            "scraping": {"timeout": 120, "strategy": "view_all", "max_categories": 10},
            "output": {"format": "json", "directory": "/tmp/output"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            config = load_config(config_file)
            assert config["scraping"]["timeout"] == 120
            assert config["scraping"]["strategy"] == "view_all"
            assert config["output"]["format"] == "json"
        finally:
            os.unlink(config_file)

    def test_load_yaml_config_file(self) -> None:
        """Test loading configuration from YAML file."""
        # This test will fail until config.py is implemented
        from src.config import load_config

        # YAML content as string (since we may not have PyYAML in test environment)
        yaml_content = """
scraping:
  timeout: 90
  strategy: categories
output:
  format: csv
  directory: /tmp/results
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            config_file = f.name

        try:
            config = load_config(config_file)
            assert config["scraping"]["timeout"] == 90
            assert config["scraping"]["strategy"] == "categories"
            assert config["output"]["format"] == "csv"
        finally:
            os.unlink(config_file)

    def test_config_file_not_found(self) -> None:
        """Test handling of non-existent configuration files."""
        # This test will fail until config.py is implemented
        from src.config import load_config

        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.json")

    def test_invalid_config_format(self) -> None:
        """Test handling of invalid configuration file formats."""
        # This test will fail until config.py is implemented
        from src.config import load_config

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content {{{")
            config_file = f.name

        try:
            with pytest.raises(ValueError):
                load_config(config_file)
        finally:
            os.unlink(config_file)


class TestConfigurationDefaults:
    """Test cases for default configuration values."""

    def test_get_default_config(self) -> None:
        """Test retrieving default configuration."""
        # This test will fail until config.py is implemented
        from src.config import get_default_config

        defaults = get_default_config()

        # Check required default values
        assert "scraping" in defaults
        assert "output" in defaults
        assert "logging" in defaults

        # Check specific defaults
        assert defaults["scraping"]["timeout"] == 120
        assert defaults["scraping"]["strategy"] == "view_all"
        assert defaults["output"]["format"] == "json"
        assert isinstance(defaults["logging"]["level"], str)

    def test_merge_config_with_defaults(self) -> None:
        """Test merging user config with defaults."""
        # This test will fail until config.py is implemented
        from src.config import merge_with_defaults

        user_config = {
            "scraping": {"timeout": 60, "strategy": "categories"},
            "output": {"directory": "/custom/path"},
        }

        merged = merge_with_defaults(user_config)

        # User overrides should be preserved
        assert merged["scraping"]["timeout"] == 60
        assert merged["scraping"]["strategy"] == "categories"
        assert merged["output"]["directory"] == "/custom/path"

        # Defaults should fill in missing values
        assert merged["output"]["format"] == "json"  # default
        assert "logging" in merged  # default section


class TestEnvironmentVariableOverrides:
    """Test cases for environment variable configuration overrides."""

    def test_env_var_override_simple_value(self) -> None:
        """Test overriding simple config values with environment variables."""
        # This test will fail until config.py is implemented
        from src.config import apply_env_overrides

        config = {"scraping": {"timeout": 120, "strategy": "view_all"}}

        # Set environment variable
        os.environ["GOOGLEMAPS_SCRAPING_TIMEOUT"] = "90"

        try:
            overridden = apply_env_overrides(config)
            assert overridden["scraping"]["timeout"] == 90
            assert overridden["scraping"]["strategy"] == "view_all"  # unchanged
        finally:
            del os.environ["GOOGLEMAPS_SCRAPING_TIMEOUT"]

    def test_env_var_override_nested_value(self) -> None:
        """Test overriding nested config values with environment variables."""
        # This test will fail until config.py is implemented
        from src.config import apply_env_overrides

        config = {"output": {"format": "json", "directory": "/tmp"}}

        # Set environment variable for nested value
        os.environ["GOOGLEMAPS_OUTPUT_FORMAT"] = "csv"

        try:
            overridden = apply_env_overrides(config)
            assert overridden["output"]["format"] == "csv"
            assert overridden["output"]["directory"] == "/tmp"  # unchanged
        finally:
            del os.environ["GOOGLEMAPS_OUTPUT_FORMAT"]

    def test_env_var_type_conversion(self) -> None:
        """Test automatic type conversion for environment variables."""
        # This test will fail until config.py is implemented
        from src.config import apply_env_overrides

        config = {"scraping": {"timeout": 120, "max_categories": 10, "verbose": False}}

        # Set environment variables with string values
        env_vars = {
            "GOOGLEMAPS_SCRAPING_TIMEOUT": "90",
            "GOOGLEMAPS_SCRAPING_MAX_CATEGORIES": "5",
            "GOOGLEMAPS_SCRAPING_VERBOSE": "true",
        }

        for key, value in env_vars.items():
            os.environ[key] = value

        try:
            overridden = apply_env_overrides(config)
            assert overridden["scraping"]["timeout"] == 90  # int conversion
            assert overridden["scraping"]["max_categories"] == 5  # int conversion
            assert overridden["scraping"]["verbose"] is True  # bool conversion
        finally:
            for key in env_vars:
                if key in os.environ:
                    del os.environ[key]


class TestConfigurationValidation:
    """Test cases for configuration validation."""

    def test_validate_required_fields(self) -> None:
        """Test validation of required configuration fields."""
        # This test will fail until config.py is implemented
        from src.config import validate_config

        # Valid config
        valid_config = {
            "scraping": {"timeout": 120, "strategy": "view_all"},
            "output": {"format": "json"},
        }
        assert validate_config(valid_config) is True

    def test_validate_invalid_strategy(self) -> None:
        """Test validation of scraping strategy values."""
        # This test will fail until config.py is implemented
        from src.config import validate_config

        invalid_config = {
            "scraping": {"timeout": 120, "strategy": "invalid_strategy"},
            "output": {"format": "json"},
        }
        assert validate_config(invalid_config) is False

    def test_validate_timeout_range(self) -> None:
        """Test validation of timeout value ranges."""
        # This test will fail until config.py is implemented
        from src.config import validate_config

        # Valid timeout
        valid_config = {
            "scraping": {"timeout": 60, "strategy": "view_all"},
            "output": {"format": "json"},
        }
        assert validate_config(valid_config) is True

        # Invalid timeout (too low)
        invalid_config_low = {
            "scraping": {"timeout": 5, "strategy": "view_all"},
            "output": {"format": "json"},
        }
        assert validate_config(invalid_config_low) is False

        # Invalid timeout (too high)
        invalid_config_high = {
            "scraping": {"timeout": 3600, "strategy": "view_all"},
            "output": {"format": "json"},
        }
        assert validate_config(invalid_config_high) is False

    def test_validate_output_format(self) -> None:
        """Test validation of output format values."""
        # This test will fail until config.py is implemented
        from src.config import validate_config

        # Valid formats
        for fmt in ["json", "csv"]:
            config = {
                "scraping": {"timeout": 120, "strategy": "view_all"},
                "output": {"format": fmt},
            }
            assert validate_config(config) is True

        # Invalid format
        invalid_config = {
            "scraping": {"timeout": 120, "strategy": "view_all"},
            "output": {"format": "xml"},
        }
        assert validate_config(invalid_config) is False


class TestConfigurationManagement:
    """Test cases for overall configuration management."""

    def test_load_config_with_env_overrides(self) -> None:
        """Test loading config file and applying environment overrides."""
        # This test will fail until config.py is implemented
        from src.config import load_config_with_overrides

        config_data = {"scraping": {"timeout": 120, "strategy": "view_all"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        # Set environment override
        os.environ["GOOGLEMAPS_SCRAPING_TIMEOUT"] = "60"

        try:
            config = load_config_with_overrides(config_file)
            assert config["scraping"]["timeout"] == 60  # overridden
            assert config["scraping"]["strategy"] == "view_all"  # from file
        finally:
            os.unlink(config_file)
            del os.environ["GOOGLEMAPS_SCRAPING_TIMEOUT"]

    def test_get_config_with_fallbacks(self) -> None:
        """Test getting configuration with multiple fallback sources."""
        # This test will fail until config.py is implemented
        from src.config import get_config

        # Test with no config file (should use defaults)
        config = get_config()
        assert config["scraping"]["timeout"] == 120  # default
        assert config["output"]["format"] == "json"  # default

    def test_config_precedence_order(self) -> None:
        """Test configuration source precedence (defaults < file < env)."""
        # This test will fail until config.py is implemented
        from src.config import get_config_with_precedence

        config_data = {
            "scraping": {
                "timeout": 120,  # will be overridden by env
                "strategy": "view_all",
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        # Set environment override (highest precedence)
        os.environ["GOOGLEMAPS_SCRAPING_TIMEOUT"] = "30"

        try:
            config = get_config_with_precedence(config_file)
            assert config["scraping"]["timeout"] == 30  # env override
            assert config["scraping"]["strategy"] == "view_all"  # from file
            assert config["output"]["format"] == "json"  # default
        finally:
            os.unlink(config_file)
            del os.environ["GOOGLEMAPS_SCRAPING_TIMEOUT"]
