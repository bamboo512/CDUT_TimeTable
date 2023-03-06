import uvicorn

if __name__ == "__main__":
    uvicorn.run("server:app", port=7669, reload=True, reload_dirs=["html_files"])
