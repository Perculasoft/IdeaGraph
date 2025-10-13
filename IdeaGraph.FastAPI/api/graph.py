from dotenv import load_dotenv
import os
from pathlib import Path
import httpx
from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date, datetime
from graph import verify_api_key, get_graph_token

router = APIRouter(tags=["Mail"])

load_dotenv()




async def get_graph_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]
