from typing import Any, TypeAlias

Redeems: TypeAlias = dict[str, dict[str, Any]]
# at the moment the Any could be specialized to str | int | list[str]