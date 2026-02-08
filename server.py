from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import threading

from selenium_runner import open_smartstore, check_logged_in

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.post("/api/open-smartstore")
def api_open():
    threading.Thread(target=open_smartstore, daemon=True).start()
    return {"ok": True}

@app.post("/api/check-login")
def api_check():
    return {"logged_in": check_logged_in()}
