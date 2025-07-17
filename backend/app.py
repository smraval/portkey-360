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
    try:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0)
        
        return image
    except Exception as e:
        logger.warning(f"Image enhancement failed: {e}")
        return image

Config.validate()

app = FastAPI(title="Portkey360 Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

if torch.cuda.is_available():
    DEVICE = "cuda"
    DTYPE = torch.float16
elif torch.backends.mps.is_available():
    DEVICE = "mps"
    DTYPE = torch.float32
else:
    DEVICE = "cpu"
    DTYPE = torch.float32

pipe: Optional[StableDiffusionPipeline] = None

def get_pipeline():
    global pipe
    if pipe is None:
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                Config.MODEL_NAME,
                torch_dtype=DTYPE,
                use_safetensors=True,
                variant="fp16" if DTYPE == torch.float16 else None
            )
            
            if not Config.ENABLE_SAFETY_CHECKER:
                pipe.safety_checker = None
            
            pipe.to(DEVICE)
            
            with torch.no_grad():
                _ = pipe("warmup", num_inference_steps=1, guidance_scale=1.0)
                
        except Exception as e:
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
        
        if Config.DEFAULT_SEED is not None:
            gen_params["generator"] = torch.Generator(device=DEVICE).manual_seed(Config.DEFAULT_SEED)
        else:
            gen_params["generator"] = torch.Generator(device=DEVICE).manual_seed(42)
        
        negative_prompt = "blurry, low quality, bad quality"
        
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
        
        return JSONResponse({
            "image_b64": b64,
            "generation_time": generation_time,
            "prompt": prompt
        })
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
