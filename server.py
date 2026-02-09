# server.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from selenium_runner import (
    open_smartstore,
    check_logged_in,
    go_product_register,
    set_category_by_query,
    go_register_and_set_category,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class CategoryReq(BaseModel):
    query: str


@app.post("/api/open-smartstore")
def api_open_smartstore():
    try:
        open_smartstore()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-login")
def api_check_login():
    try:
        return {"logged_in": bool(check_logged_in())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/go-register")
def api_go_register():
    try:
        go_product_register()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/set-category")
def api_set_category(req: CategoryReq):
    try:
        set_category_by_query(req.query)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 원샷 엔드포인트: 상품등록 이동 + 카테고리 선택까지 한 번에
@app.post("/api/go-register-and-set-category")
def api_go_register_and_set_category(req: CategoryReq):
    try:
        go_register_and_set_category(req.query)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
