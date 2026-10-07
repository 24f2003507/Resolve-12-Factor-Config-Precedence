from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Defaults
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# 2. YAML layer
with open("config.development.yaml") as f:
    yaml_cfg = yaml.safe_load(f)
    config.update(yaml_cfg)

# 3. .env layer
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                if k == "NUM_WORKERS":
                    config["workers"] = int(v)

# 4. OS env vars (APP_* prefix)
for k, v in os.environ.items():
    if k.startswith("APP_"):
        key = k.replace("APP_", "").lower()
        config[key] = v

def coerce(key, value):
    if key in ["port", "workers"]:
        return int(value)
    if key == "debug":
        return str(value).lower() in ["1", "true", "yes", "on"]
    return str(value)

@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    final = config.copy()

    # 5. CLI overrides
    for item in set:
        k, v = item.split("=", 1)
        final[k] = coerce(k, v)

    # mask secret
    final["api_key"] = "****"

    return final
