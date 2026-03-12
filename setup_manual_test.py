import json
from pathlib import Path

# Create a dummy AppID snapshot to bypass the 404 network error during initial test
snapshot_path = Path("data") / "app_list_manual_test.json"
snapshot_path.parent.mkdir(exist_ok=True)

dummy_data = [
    {"appid": 10, "name": "Counter-Strike"},
    {"appid": 20, "name": "Team Fortress Classic"},
    {"appid": 999999, "name": "Non-Existent Game"} 
]

with open(snapshot_path, "w") as f:
    json.dump(dummy_data, f)

print(f"Created manual snapshot at {snapshot_path}")
