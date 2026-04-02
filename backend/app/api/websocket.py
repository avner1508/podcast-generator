import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.job_manager import job_manager

router = APIRouter()


@router.websocket("/api/ws/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        await websocket.close(code=4004, reason="Job not found")
        return

    await websocket.accept()
    queue = job_manager.subscribe(job_id)

    try:
        # Send current state immediately
        await websocket.send_json({
            "job_id": job.id,
            "podcast_id": job.podcast_id,
            "stage": job.stage.value,
            "progress": job.progress,
            "error": job.error,
        })

        while True:
            try:
                update = await asyncio.wait_for(queue.get(), timeout=30)
                await websocket.send_json(update)
                if update.get("stage") in ("completed", "failed"):
                    break
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        pass
    finally:
        job_manager.unsubscribe(job_id, queue)
