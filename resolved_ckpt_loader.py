
import comfy.model_management as mm
from .resolved_core import ensure_model

class ResolvedCheckpointLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": ("STRING", {"default": ""}),
                "vae_name":  ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load"
    CATEGORY = "loaders/resolved"

    def load(self, ckpt_name, vae_name):
        if not ckpt_name:
            raise ValueError("ckpt_name is empty")
        ckpt_path = ensure_model("checkpoints", ckpt_name)
        vae_path  = ensure_model("vae", vae_name) if vae_name else None
        model, clip, vae = mm.load_checkpoint(ckpt_path, vae_override=vae_path)
        return (model, clip, vae)

NODE_CLASS_MAPPINGS = {"ResolvedCheckpointLoader": ResolvedCheckpointLoader}
NODE_DISPLAY_NAME_MAPPINGS = {"ResolvedCheckpointLoader": "Resolved Checkpoint Loader (R2)"}
