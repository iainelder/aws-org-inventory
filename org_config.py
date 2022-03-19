from typing import Any, Dict


class InvalidConfigError(Exception):
    pass


class OrgConfig:
    pass

    def __init__(self, config: Dict[str, Any]) -> None:
        if config == {}:
            raise InvalidConfigError(config)
        pass
