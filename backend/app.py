import io
import base64
import time
from typing import Optional
import logging

import torch
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageEnhance

from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

def enhance_prompt_for_panorama(prompt: str) -> str:
    return f"{prompt}, less grainy, less pixelated"

def enhance_image_quality(image: Image.Image) -> Image.Image:
    """Balanced brightness and natural colors"""
    try:
        # Moderate brightness increase
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.3)  # 30% brighter
        
        # Gentle contrast boost
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)  # Slight contrast
        
        # Natural color enhancement - not oversaturated
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0)  # Keep natural colors
        
        return image
    except Exception as e:
        logger.warning(f"Image enhancement failed: {e}")
        return image

# Safe device detection
def get_device_and_dtype():
    if torch.cuda.is_available():
        return "cuda", torch.float16
    elif hasattr(torch.backends, 'mps') and hasattr(torch.backends.mps, 'is_available') and torch.backends.mps.is_available():
        return "mps", torch.float32
    else:
        return "cpu", torch.float32

# Safe cache clearing
def clear_cache(device):
    try:
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif device == "mps" and hasattr(torch, 'mps') and hasattr(torch.mps, 'empty_cache'):
            torch.mps.empty_cache()
    except Exception as e:
        logger.warning(f"Cache clearing failed: {e}")

Config.validate()

app = FastAPI(title="Portkey360 Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

DEVICE, DTYPE = get_device_and_dtype()
pipe: Optional[StableDiffusionPipeline] = None

def get_pipeline():
    global pipe
    if pipe is None:
        try:
            logger.info(f"Loading model {Config.MODEL_NAME} on device {DEVICE}")
            pipe = StableDiffusionPipeline.from_pretrained(
                Config.MODEL_NAME,
                torch_dtype=DTYPE,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            pipe.to(DEVICE)
            pipe.enable_attention_slicing()
            logger.info("Model loaded successfully")
                
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")

    return pipe

@app.get("/health")
async def health_check():
    return {"status": "healthy", "device": DEVICE}

@app.post("/generate")
async def generate(prompt: str = Body(..., embed=True)):
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    start_time = time.time()
    
    try:
        pipeline = get_pipeline()
        enhanced_prompt = enhance_prompt_for_panorama(prompt)
        gen_params = Config.get_generation_params()
        
        # Set seed
        seed = Config.DEFAULT_SEED if Config.DEFAULT_SEED is not None else 42
        gen_params["generator"] = torch.Generator(device=DEVICE).manual_seed(seed)
        
        negative_prompt = "blurry, low quality, bad quality"
        
        # Clear cache before generation
        clear_cache(DEVICE)
        
        with torch.no_grad():
            result = pipeline(
                enhanced_prompt, 
                negative_prompt=negative_prompt,
                **gen_params
            )
        
        image = result.images[0]
        image = enhance_image_quality(image)
        
        buf = io.BytesIO()
        image.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        generation_time = time.time() - start_time
        
        # Clear cache after generation
        clear_cache(DEVICE)
        
        return JSONResponse({
            "image_b64": b64,
            "generation_time": generation_time,
            "prompt": prompt,
            "dimensions": f"{gen_params['width']}x{gen_params['height']}",
            "panorama_mode": True
        })
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        clear_cache(DEVICE)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
