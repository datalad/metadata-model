from typing import Dict, List, Union


JSONObject = Union[
    None, bool, int, float, str,
    List["JSONObject"],
    Dict[str, "JSONObject"]
]
