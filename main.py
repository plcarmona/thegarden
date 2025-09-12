from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.huerta import router as huerta_router
from app.weather_router import router as weather_router
from app.calendar_router import router as calendar_router

app = FastAPI(title="The Garden", description="Garden planning and management application")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(huerta_router, prefix="/api/huerta", tags=["huerta"])
app.include_router(weather_router, prefix="/api/clima", tags=["clima"])
app.include_router(calendar_router, prefix="/api/calendario", tags=["calendario"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page with garden map interface"""
    return templates.TemplateResponse("index.html", {"request": request})