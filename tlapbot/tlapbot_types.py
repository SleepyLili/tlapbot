from typing import Any, TypeAlias

Redeem: TypeAlias = dict[str, dict[str, Any]]
# at the moment the Any could be specialized to str | int | list[str]
Redeems: TypeAlias = dict[str, Redeem]