"""Configuration management for API keys and settings."""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Configuration manager for Symboval."""

    CONFIG_DIR = Path.home() / ".symboval"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        """Initialize configuration manager."""
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file if it exists."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config file: {e}")
                self._config = {}
        else:
            self._config = {}

    def _save_config(self):
        """Save configuration to file."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save config file: {e}")

    def get_api_key(self, provider: str = "openrouter") -> Optional[str]:
        """Get API key for a provider.

        Args:
            provider: Name of the provider (default: "openrouter")

        Returns:
            API key if found, None otherwise
        """
        # First check environment variable
        env_var = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var)

        if api_key:
            return api_key

        # Then check config file
        return self._config.get("api_keys", {}).get(provider)

    def set_api_key(self, api_key: str, provider: str = "openrouter"):
        """Set API key for a provider.

        Args:
            api_key: The API key to store
            provider: Name of the provider (default: "openrouter")
        """
        if "api_keys" not in self._config:
            self._config["api_keys"] = {}

        self._config["api_keys"][provider] = api_key
        self._save_config()

    def remove_api_key(self, provider: str = "openrouter"):
        """Remove API key for a provider.

        Args:
            provider: Name of the provider (default: "openrouter")
        """
        if "api_keys" in self._config and provider in self._config["api_keys"]:
            del self._config["api_keys"][provider]
            self._save_config()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self._config.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set a configuration setting.

        Args:
            key: Setting key
            value: Setting value
        """
        if "settings" not in self._config:
            self._config["settings"] = {}

        self._config["settings"][key] = value
        self._save_config()

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings.

        Returns:
            Dictionary of all settings (excluding API keys)
        """
        return self._config.get("settings", {}).copy()

    def clear_all(self):
        """Clear all configuration (use with caution)."""
        self._config = {}
        self._save_config()


# Global config instance
_config = Config()


def set_api_key(api_key: str, provider: str = "openrouter"):
    """Set API key for a provider.

    Args:
        api_key: The API key to store
        provider: Name of the provider (default: "openrouter")

    Example:
        >>> import symboval
        >>> symboval.set_api_key("sk-or-v1-xxx")
    """
    _config.set_api_key(api_key, provider)


def get_api_key(provider: str = "openrouter") -> Optional[str]:
    """Get API key for a provider.

    Args:
        provider: Name of the provider (default: "openrouter")

    Returns:
        API key if found, None otherwise

    Example:
        >>> import symboval
        >>> api_key = symboval.get_api_key()
    """
    return _config.get_api_key(provider)


def remove_api_key(provider: str = "openrouter"):
    """Remove API key for a provider.

    Args:
        provider: Name of the provider (default: "openrouter")

    Example:
        >>> import symboval
        >>> symboval.remove_api_key()
    """
    _config.remove_api_key(provider)
