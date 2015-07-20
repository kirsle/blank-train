from __future__ import unicode_literals

from yamlsettings import YamlSettings

# Singleton config
_config = None

def get_config(run_env="train"):
    global _config
    if _config is not None:
        return _config

    app_settings = YamlSettings("defaults.yml", "settings.yml",
        default_section=run_env)
    return app_settings.get_settings(run_env)
