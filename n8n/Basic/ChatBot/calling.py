from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx # Better for async than 'requests'
import uvicorn

app = FastAPI()

# Setup templates and static files (for your avatar image)
templates = Jinja2Templates(directory="templates")

# REPLACE with your actual n8n URL
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/54bb4e6b-45fa-4267-af28-ad70ec113231"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/send_message")
async def send_message(request: Request):
    user_data = await request.json()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(N8N_WEBHOOK_URL, json=user_data, timeout=60.0)
    
        print(f"DEBUG: Status Code: {response.status_code}")
        if not response.text.strip():
            return {"output": "n8n returned an empty response. Check your 'Respond to Webhook' node settings."}

        try:
            return response.json()
        except Exception:
            return {"output": response.text}
            
        # 1. Check if n8n returned a 404 or 500 error
        if response.status_code != 200:
            return {"output": f"n8n Error ({response.status_code}): {response.text}"}

        # 2. Try to parse JSON safely
        try:
            return response.json()
        except Exception:
            return {"output": f"n8n sent non-JSON text: {response.text}"}

        except Exception as e:
            return {"output": f"Bridge Connection Failed: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)