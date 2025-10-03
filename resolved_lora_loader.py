
import comfy.sd
from .resolved_core import ensure_model

class ResolvedLoraLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "clip":  ("CLIP",),
                "lora_name": ("STRING", {"default": ""}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip":  ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("MODEL","CLIP")
    FUNCTION = "apply"
    CATEGORY = "loaders/resolved"

    def apply(self, model, clip, lora_name, strength_model, strength_clip):
        if lora_name:
            lora_path = ensure_model("loras", lora_name)
            model, clip = comfy.sd.load_lora_for_models(model, clip, lora_path, strength_model, strength_clip)
        return (model, clip)

NODE_CLASS_MAPPINGS = {"ResolvedLoraLoader": ResolvedLoraLoader}
NODE_DISPLAY_NAME_MAPPINGS = {"ResolvedLoraLoader": "Resolved LoRA Loader (R2)"}
