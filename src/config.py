"""Configuration Management Module for Google Maps Mall Scraper.

Handles loading, validation, and management of application configuration
from files, environment variables, and defaults.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union


def load_config(config_file: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from a file (JSON or YAML).

    Args:
        config_file: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is invalid
    """  # noqa: E501
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Try JSON first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try YAML if available
    try:
        import yaml  # type: ignore[import-untyped]

        result = yaml.safe_load(content)
        if isinstance(result, dict):
            return result
        else:
            raise ValueError(f"Invalid configuration file format: {config_file}")
    except ImportError:
        # YAML not available, re-raise JSON error
        raise ValueError(f"Invalid configuration file format: {config_file}")
    except Exception:
        raise ValueError(f"Invalid configuration file format: {config_file}")


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values.

    Returns:
        Default configuration dictionary
    """
    return {
        "scraping": {
            "timeout": 120,
            "strategy": "view_all",
            "max_categories": 10,
            "verbose": False,
        },
        "output": {
            "format": "json",
            "directory": "./output",
            "filename_template": "mall_scrape_{timestamp}.json",  # noqa: E501,
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "anti_bot": {"min_delay": 0.5, "max_delay": 2.0, "user_agent_rotation": True},
    }


def merge_with_defaults(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user configuration with defaults.

    Args:
        user_config: User-provided configuration

    Returns:
        Merged configuration with defaults filled in
    """
    defaults = get_default_config()

    def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    return deep_merge(defaults, user_config)


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration.

    Environment variables should be prefixed with 'GOOGLEMAPS_' and use
    nested keys separated by underscores. For example:  # noqa: E501
    GOOGLEMAPS_SCRAPING_TIMEOUT=60

    Args:
        config: Configuration dictionary

    Returns:
        Configuration with environment overrides applied
    """
    prefix = "GOOGLEMAPS_"
    result = config.copy()

    for env_key, env_value in os.environ.items():
        if env_key.startswith(prefix):
            # Remove prefix and convert to nested keys
            config_key = env_key[len(prefix) :].lower()

            # Split into section and key (only split on first underscore)
            if "_" in config_key:
                section, key = config_key.split("_", 1)
            else:
                section = config_key
                key = None

            value = _convert_env_value(env_value)

            # Ensure section exists
            if section not in result:
                result[section] = {}

            # Set the value
            if key is None:
                # If no key, replace the entire section
                result[section] = value
            else:
                # Set specific key in section
                result[section][key] = value

    return result


def _convert_env_value(value: str) -> Union[str, int, float, bool]:
    """Convert environment variable string to appropriate type.

    Args:
        value: String value from environment

    Returns:
        Converted value (int, float, bool, or str)
    """
    value_lower = value.lower()

    # Try boolean conversion
    if value_lower in ("true", "1", "yes", "on"):
        return True
    elif value_lower in ("false", "0", "no", "off"):
        return False

    # Try int conversion
    try:
        return int(value)
    except ValueError:
        pass

    # Try float conversion
    try:
        return float(value)
    except ValueError:
        pass

    # Return as string
    return value


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration values.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        # Validate scraping section
        if "scraping" in config:
            scraping = config["scraping"]

            # Validate timeout
            timeout = scraping.get("timeout", 120)
            if not isinstance(timeout, int) or not (10 <= timeout <= 600):
                return False

            # Validate strategy
            strategy = scraping.get("strategy", "view_all")
            if strategy not in ["view_all", "categories"]:
                return False

            # Validate max_categories
            max_categories = scraping.get("max_categories", 10)
            if not isinstance(max_categories, int) or max_categories < 1:
                return False

        # Validate output section
        if "output" in config:
            output = config["output"]

            # Validate format
            output_format = output.get("format", "json")
            if output_format not in ["json", "csv"]:
                return False

        # Validate logging section
        if "logging" in config:
            logging = config["logging"]

            # Validate log level
            level = logging.get("level", "INFO")
            if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                return False

        return True

    except Exception:
        return False


def load_config_with_overrides(
    config_file: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Load configuration from file and apply environment overrides.

    Args:
        config_file: Optional path to config file

    Returns:
        Complete configuration with defaults, file, and env overrides
    """
    # Start with defaults
    config = get_default_config()

    # Load from file if provided
    if config_file:
        file_config = load_config(config_file)
        config = merge_with_defaults(file_config)

    # Apply environment overrides
    config = apply_env_overrides(config)

    # Validate final configuration
    if not validate_config(config):
        raise ValueError("Invalid configuration")

    return config


def get_config(config_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Get configuration with intelligent fallbacks.

    Looks for configuration in this order:
    1. Specified config file
    2. Default config file in current directory (config.json, config.yaml)
    3. Environment variables
    4. Defaults

    Args:
        config_file: Optional specific config file path

    Returns:
        Complete configuration
    """
    # If specific file provided, use it
    if config_file:
        return load_config_with_overrides(config_file)

    # Look for default config files
    default_files = ["config.json", "config.yaml", "config.yml"]
    for filename in default_files:
        if Path(filename).exists():
            return load_config_with_overrides(filename)

    # No config file found, use defaults + env overrides
    config = get_default_config()
    config = apply_env_overrides(config)

    if not validate_config(config):
        raise ValueError("Invalid configuration")

    return config


def get_config_with_precedence(
    config_file: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Get configuration demonstrating precedence order.

    Precedence (highest to lowest):
    1. Environment variables
    2. Configuration file
    3. Defaults

    Args:
        config_file: Optional config file path

    Returns:
        Configuration with proper precedence
    """
    return get_config(config_file)
