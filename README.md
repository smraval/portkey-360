# portkey360° 
your imagination, brought to life in 360°. describe any scene in words and explore it as a full 360° panorama you can look around in your browser.

## what it does
✍️ type a description → 🖼️ get a 360° panorama → 🕹️ explore in 3D

## how to use

### 1. clone and setup
```bash
git clone <this-repo>
cd portkey360
chmod +x start.sh
./start.sh
```

### 2. open your browser
- go to http://localhost:3000
- type a scene description
- click "generate"
- explore your 360° pano!


## manual setup (if start.sh doesn't work)

**backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**frontend:**
```bash
cd frontend
npm install
npm run dev
```

_then_ open via http://localhost:3000


## tech stack

- **model**: hugging face stable diffusion 2.1
- **backend**: fastAPI, pyTorch, diffusers library
- **frontend**: next.js, three.js, react three fiber
- **3D rendering**: webGL panorama viewer


