
# comfy_resolved_loaders

Custom nodes for ComfyUI that **select** and **lazy-download** models from Cloudflare R2 (S3-compatible) and cache them locally.

## Features
- Dropdown selectors with **Refresh** to list objects from R2 (`checkpoints/`, `vae/`, `loras/`)
- Lazy download on first use, cached at `$MODELS_DIR`
- Simple env-based configuration; Docker-friendly

## Install
1. Copy folder `comfy_resolved_loaders/` into `ComfyUI/custom_nodes/`.
2. Install deps:
   ```bash
   pip install -r ComfyUI/custom_nodes/comfy_resolved_loaders/requirements.txt
   ```
3. Set env vars (in shell, systemd or Docker):
   ```bash
   export MODELS_DIR="/workspace/ComfyUI/models"
   export R2_ENDPOINT="https://<ACCOUNT_ID>.r2.cloudflarestorage.com"
   export R2_ACCESS_KEY="<ACCESS_KEY_ID>"
   export R2_SECRET_KEY="<SECRET_ACCESS_KEY>"
   export R2_BUCKET="comfyui-models"
   ```
4. Restart ComfyUI.

## Nodes
- **R2 Catalog Refresh** — button node to refresh the catalog from R2.
- **R2 Model Selector (Dropdowns)** — dropdowns for `checkpoint`, `vae`, `lora`.
- **Resolved Checkpoint Loader (R2)** — ensures files and loads (`MODEL`, `CLIP`, `VAE`).
- **Resolved LoRA Loader (R2)** — ensures LoRA file and applies to model/clip.

## Usage
1. Place **R2 Catalog Refresh**, click it once after start.
2. Place **R2 Model Selector**, pick names from dropdowns.
3. Feed outputs into **Resolved Checkpoint Loader** and **Resolved LoRA Loader**.
4. Run. On first run files are downloaded to `$MODELS_DIR/<kind>/` and reused afterwards.

## Notes
- The catalog fetch ignores nested folders below each prefix to keep dropdowns simple.
- You can extend with ControlNet/VAE loaders by following the same pattern.
- For large files ensure stable network; R2 egress is free, but download time depends on your link.

MIT — use at your own risk.
