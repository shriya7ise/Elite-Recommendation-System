# backend/main.py (FastAPI)
import os
import sys
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from dotenv import load_dotenv

current_dir = Path(__file__).parent
global_env = current_dir.parent / '.env'
local_env = current_dir / '.env'

if global_env.exists():
    load_dotenv(global_env)
    print(f"Loaded .env from global directory: {global_env}")
elif local_env.exists():
    load_dotenv(local_env)
    print(f"Loaded .env from backend directory: {local_env}")
else:
    print("No .env file found in global or backend directory")

app = FastAPI()

# CORS middleware - configure for your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables - set these in your .env file
PLACID_API_KEY = os.getenv("PLACID_API_KEY")
PLACID_TEMPLATE_ID = os.getenv("PLACID_TEMPLATE_ID")

print(f"🔑 API Key configured: {'✅ Yes' if PLACID_API_KEY else '❌ No'}")
print(f"📋 Template ID configured: {'✅ Yes' if PLACID_TEMPLATE_ID else '❌ No'}")

class CreativeRequest(BaseModel):
    template_id: str
    modifications: Dict[str, Any]
    create_now: bool = True

@app.get("/")
def read_root():
    return {"message": "Placid API Backend is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "placid_api_configured": bool(PLACID_API_KEY),
        "template_configured": bool(PLACID_TEMPLATE_ID)
    }

@app.post("/api/generate-ad")
def generate_ad(req: CreativeRequest):
    if not PLACID_API_KEY:
        raise HTTPException(status_code=500, detail="Placid API key not configured")
    
    # Use template_id from request or fallback to environment variable
    template_id = req.template_id or PLACID_TEMPLATE_ID
    
    if not template_id:
        raise HTTPException(status_code=400, detail="Template ID not provided")
    
    try:
        # Placid API endpoint
        url = f"https://api.placid.app/api/rest/{template_id}"
        
        headers = {
            "Authorization": f"Bearer {PLACID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Clean up the modifications data - ensure all values are strings
        cleaned_modifications = {}
        for key, value in req.modifications.items():
            if value is not None:
                cleaned_modifications[key] = str(value)
        
        payload = {
            "create_now": req.create_now,
            "modifications": cleaned_modifications
        }
        
        print(f"Making request to Placid API: {url}")
        print(f"Template ID: {template_id}")
        print(f"Modifications sent to Placid:")
        for key, value in cleaned_modifications.items():
            print(f"  - {key}: {value}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Placid API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Placid API Response: {response_data}")
            return response_data
        else:
            error_text = response.text
            print(f"Placid API error: {response.status_code} - {error_text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Placid API error: {error_text}"
            )
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Add a new endpoint to help debug template fields
@app.get("/api/template-info/{template_id}")
def get_template_info(template_id: str):
    if not PLACID_API_KEY:
        raise HTTPException(status_code=500, detail="Placid API key not configured")
    
    try:
        url = f"https://api.placid.app/api/rest/templates/{template_id}"
        headers = {"Authorization": f"Bearer {PLACID_API_KEY}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get template info: {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)