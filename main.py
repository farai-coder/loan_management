from fastapi import FastAPI
from routers import user,admin,login,loan_managent
import uvicorn

app = FastAPI()

# add all the routes
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(loan_managent.router, prefix="/loan", tags=["loan Management"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(login.router, prefix="/login", tags=["login"])

# add cors middleware

@app.get("/")
def read_root():
    return {"message": "Welcome to the loan management system!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
