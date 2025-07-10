import json
import os
from enum import Enum
from typing import Any, Dict
from threading import Lock

class Setting(Enum):
    MAX_SECTIONS_PER_CLASS = "max_sections_per_class"
    MAX_STUDENTS_PER_CLASS = "max_students_per_class"
    MAX_INSTRUCTORS_PER_CLASS = "max_instructors_per_class"
    MIN_STUDENTS_PER_CLASS = "min_students_per_class"
    MAX_CLASSES_PER_INSTRUCTOR = "max_classes_per_instructor"
    PRIORITIZE_FIRST_CHOICE = "prioritize_first_choice"


class Settings:
    """ Singleton class to manage application settings. """
    _instance = None
    _lock = Lock()  # Ensure thread-safe singleton access

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Settings, cls).__new__(cls)
                    cls._instance.__init__()
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            # Settings with defaults
            self._settings_file = "settings.json"
            self.settings = {}
            self._defaults = {
                Setting.MAX_SECTIONS_PER_CLASS: 3,  # Default max sections per class
                Setting.MAX_STUDENTS_PER_CLASS: 20,
                Setting.MAX_INSTRUCTORS_PER_CLASS: 2,
                Setting.MIN_STUDENTS_PER_CLASS: 6,
                Setting.MAX_CLASSES_PER_INSTRUCTOR: 2,
                Setting.PRIORITIZE_FIRST_CHOICE: True
            }
            self.load_settings()
            self._initialized = True

    # UNTESTED:
    def _load_settings(self, file_path):
        """Load settings from file, using defaults if file doesn't exist"""
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, 'r') as f:
                    self._settings = json.load(f)
                # print(f"Settings loaded from {self._settings_file}")
            except (json.JSONDecodeError, IOError) as e:
                # print(f"Error loading settings: {e}, using defaults")
                self._settings = self._defaults.copy()
        else:
            self._settings = self._defaults.copy()
            self._save_settings()

    def _save_settings(self):
        """Save current settings to file"""
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
            print(f"Settings saved to {self._settings_file}")
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get_setting(self, key: Setting) -> Any:
        """Get a setting value dynamically"""
        return self._settings.get(key.value, self._defaults.get(key.value))
    
    def set_setting(self, key: Setting, value: Any) -> None:
        """Set a setting value and save to file"""
        self._settings[key.value] = value
        self._save_settings()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        return self._settings.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self._settings = self._defaults.copy()
        self._save_settings()
    
    def reload_from_file(self) -> None:
        """Reload settings from file (useful if file was modified externally)"""
        self._load_settings()

    def reset_settings(self):
        self.reset_to_defaults()