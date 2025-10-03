
import os, time, threading
import boto3
from botocore.config import Config

R2_ENDPOINT = os.environ.get("R2_ENDPOINT")
R2_ACCESS   = os.environ.get("R2_ACCESS_KEY")
R2_SECRET   = os.environ.get("R2_SECRET_KEY")
R2_BUCKET   = os.environ.get("R2_BUCKET", "comfyui-models")

_session = boto3.session.Session(
    aws_access_key_id=R2_ACCESS,
    aws_secret_access_key=R2_SECRET,
)
_s3 = _session.client("s3", endpoint_url=R2_ENDPOINT, config=Config(retries={"max_attempts": 3}))

_cache = {"checkpoints": [], "vae": [], "loras": [], "controlnet": []}
_cache_ts = 0.0
_lock = threading.Lock()

def _list_prefix(prefix: str):
    keys = []
    token = None
    while True:
        kwargs = {"Bucket": R2_BUCKET, "Prefix": prefix}
        if token:
            kwargs["ContinuationToken"] = token
        resp = _s3.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/") or key == prefix:
                continue
            name = key[len(prefix):]
            if "/" in name:
                # skip nested folders for dropdown simplicity
                continue
            keys.append(name)
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return sorted(keys, key=str.lower)

def refresh_catalog():
    global _cache_ts
    with _lock:
        _cache["checkpoints"] = _list_prefix("checkpoints/")
        _cache["vae"]         = _list_prefix("vae/")
        _cache["loras"]       = _list_prefix("loras/")
        _cache["controlnet"]  = _list_prefix("controlnet/")
        _cache_ts = time.time()

# Try initial refresh (non-fatal if env not ready yet)
try:
    refresh_catalog()
except Exception:
    pass

class R2ModelSelect:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": ("STRING", {"default": (_cache["checkpoints"][0] if _cache["checkpoints"] else ""), "choices": _cache["checkpoints"]}),
                "vae_name":  ("STRING", {"default": "", "choices": ([''] + _cache['vae'])}),
                "lora_name": ("STRING", {"default": "", "choices": ([''] + _cache['loras'])}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("ckpt_name", "vae_name", "lora_name")
    FUNCTION = "select"
    OUTPUT_NODE = False
    CATEGORY = "loaders/resolved"

    def select(self, ckpt_name, vae_name, lora_name):
        return (ckpt_name, vae_name, lora_name)

    @classmethod
    def IS_CHANGED(s, **kwargs):
        # Force UI rerender when catalog timestamp changes
        return float(_cache_ts)

class R2RefreshCatalog:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {}}

    RETURN_TYPES = ()
    FUNCTION = "refresh"
    CATEGORY = "loaders/resolved"

    def refresh(self):
        refresh_catalog()
        return ()

NODE_CLASS_MAPPINGS = {
    "R2ModelSelect": R2ModelSelect,
    "R2RefreshCatalog": R2RefreshCatalog,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "R2ModelSelect": "R2 Model Selector (Dropdowns)",
    "R2RefreshCatalog": "R2 Catalog Refresh",
}
