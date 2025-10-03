
import os, threading
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

MODELS_DIR = os.environ.get("MODELS_DIR", "/workspace/ComfyUI/models")
R2_ENDPOINT = os.environ.get("R2_ENDPOINT")
R2_ACCESS   = os.environ.get("R2_ACCESS_KEY")
R2_SECRET   = os.environ.get("R2_SECRET_KEY")
R2_BUCKET   = os.environ.get("R2_BUCKET", "comfyui-models")

if not all([R2_ENDPOINT, R2_ACCESS, R2_SECRET, R2_BUCKET]):
    raise RuntimeError("R2 env vars missing: R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET")

# boto3 client for Cloudflare R2 (S3-compatible)
_session = boto3.session.Session(
    aws_access_key_id=R2_ACCESS,
    aws_secret_access_key=R2_SECRET,
    region_name="auto",
)
_s3 = _session.client("s3", endpoint_url=R2_ENDPOINT, config=Config(
    connect_timeout=30, read_timeout=600, retries={"max_attempts": 5, "mode": "standard"}
))

# In-process file locks to avoid double-downloads
_locks = {}
_guard = threading.Lock()

def _file_lock(path: str) -> threading.Lock:
    with _guard:
        lk = _locks.get(path)
        if lk is None:
            lk = threading.Lock()
            _locks[path] = lk
        return lk

def ensure_model(kind: str, name: str) -> str:
    """
    Ensure a model file exists locally, else fetch from R2.
    kind: 'checkpoints' | 'vae' | 'loras' | 'controlnet' | ...
    name: filename, e.g. 'model.safetensors'
    returns local path
    """
    local_dir = os.path.join(MODELS_DIR, kind)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, name)

    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path

    key = f"{kind}/{name}"
    lk = _file_lock(local_path)
    with lk:
        # double check inside lock
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            return local_path

        tmp = local_path + ".part"
        try:
            with open(tmp, "wb") as f:
                _s3.download_fileobj(R2_BUCKET, key, f)
            os.replace(tmp, local_path)
            return local_path
        except ClientError as e:
            # cleanup partial
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass
            raise RuntimeError(f"Failed to fetch {key} from R2: {e}")
