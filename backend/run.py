import sys
import asyncio
import uvicorn

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    # RELOAD MUST BE FALSE ON WINDOWS FOR PLAYWRIGHT TO WORK
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, workers=1)
