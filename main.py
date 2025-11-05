from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import members, expenses

app = FastAPI(title="Expense Tracker Backend")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable Jinja2 template engine
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(members.router)
app.include_router(expenses.router)

