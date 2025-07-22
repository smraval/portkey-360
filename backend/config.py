import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    MODEL_NAME: str = "runwayml/stable-diffusion-v1-5"
    
    DEFAULT_INFERENCE_STEPS: int = int(os.getenv("INFERENCE_STEPS", "20"))
    DEFAULT_GUIDANCE_SCALE: float = float(os.getenv("GUIDANCE_SCALE", "7.5"))
    DEFAULT_WIDTH: int = int(os.getenv("IMAGE_WIDTH", "768"))
    DEFAULT_HEIGHT: int = int(os.getenv("IMAGE_HEIGHT", "512"))
    DEFAULT_SEED: Optional[int] = int(os.getenv("DEFAULT_SEED", "42")) if os.getenv("DEFAULT_SEED") else None
    
    ENABLE_SAFETY_CHECKER: bool = os.getenv("ENABLE_SAFETY_CHECKER", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_generation_params(cls, **kwargs):
        return {
            "num_inference_steps": kwargs.get("num_inference_steps", cls.DEFAULT_INFERENCE_STEPS),
            "guidance_scale": kwargs.get("guidance_scale", cls.DEFAULT_GUIDANCE_SCALE),
            "width": kwargs.get("width", cls.DEFAULT_WIDTH),
            "height": kwargs.get("height", cls.DEFAULT_HEIGHT),
            "generator": kwargs.get("generator", None),
            "num_images_per_prompt": 1,
        }
    
    @classmethod
    def validate(cls):
        if cls.DEFAULT_WIDTH % 8 != 0 or cls.DEFAULT_HEIGHT % 8 != 0:
            raise ValueError("Image dimensions must be multiples of 8")
        if cls.DEFAULT_INFERENCE_STEPS < 1:
            raise ValueError("Inference steps must be at least 1")
        if cls.DEFAULT_GUIDANCE_SCALE < 1.0:
            raise ValueError("Guidance scale must be at least 1.0") 