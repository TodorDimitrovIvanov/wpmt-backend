from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import log, db, user, website, account, backup, php, ssh
import uvicorn

app = FastAPI()
# Importing multiple routers
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#import-fastapi
for item in [log, db, user, website, account, backup, php, ssh]:
    app.include_router(item.router)


origins = [
    "http://localhost:13332",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    # TODO: Add error handling for when the default port is not available
    uvicorn.run(app, host='localhost', port=13332)