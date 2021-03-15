from typing import Dict, List, Union


JSONObject = Union[int, float, str, List["JSONObject"], Dict[str, "JSONObject"]]
