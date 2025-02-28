# api.py
from fastapi import FastAPI, BackgroundTasks
import logging
from workflow import process_image_batch, generate_download_file, process_restart_batch
from database import update_ai_sort_order, update_initial_sort_order, check_json_status, fix_json_data
from aws_s3 import upload_file_to_space
from logging_config import setup_job_logger
import os
import uuid
import ray

app = FastAPI()

# Initialize Ray once at startup
ray.init(ignore_reinit_error=True)

# Define default logger for non-job contexts
default_logger = logging.getLogger(__name__)
if not default_logger.handlers:
    default_logger.setLevel(logging.INFO)

async def run_job_with_logging(job_func, *args, file_id=None, **kwargs):
    logger, log_filename = setup_job_logger(job_id=file_id or str(uuid.uuid4()))
    logger.info(f"Starting job {job_func.__name__} for FileID: {file_id}")
    result = await job_func(*args, logger=logger, file_id=file_id, **kwargs)  # Await the async function
    if os.path.exists(log_filename):
        upload_url = upload_file_to_space(log_filename, f"job_logs/job_{file_id}.log", logger=logger, file_id=file_id)
        logger.info(f"Log file uploaded to: {upload_url}")
    logger.info(f"Job {job_func.__name__} completed")
    return result

@app.get("/check_json_status/{file_id}")
async def api_check_json_status(file_id: str):
    logger, _ = setup_job_logger(job_id=file_id)
    logger.info(f"Checking JSON status for FileID: {file_id}")
    return check_json_status(file_id, logger=logger)

@app.get("/initial_sort/{file_id}")
async def api_initial_sort(file_id: str):
    logger, _ = setup_job_logger(job_id=file_id)
    logger.info(f"Running initial sort for FileID: {file_id}")
    return update_initial_sort_order(file_id, logger=logger)

@app.post("/update_sort_llama/")
async def api_update_sort(background_tasks: BackgroundTasks, file_id_db: str):
    logger, _ = setup_job_logger(job_id=file_id_db)
    logger.info(f"Queueing AI sort order update for FileID: {file_id_db}")
    background_tasks.add_task(run_job_with_logging, update_ai_sort_order, file_id_db, file_id=file_id_db)
    return {"message": f"Sort order update for FileID: {file_id_db} initiated", "status": "processing"}

@app.post("/fix_json_data/")
async def api_fix_json_data(background_tasks: BackgroundTasks, file_id: str = None, limit: int = 1000):
    job_id = file_id or str(uuid.uuid4())
    logger, _ = setup_job_logger(job_id=job_id)
    logger.info(f"Queueing JSON fix" + (f" for FileID: {file_id}" if file_id else " globally"))
    result = fix_json_data(background_tasks, file_id, limit, logger=logger)
    return result

@app.post("/restart-failed-batch/")
async def api_process_restart(background_tasks: BackgroundTasks, file_id_db: str):
    logger, _ = setup_job_logger(job_id=file_id_db)
    logger.info(f"Queueing restart of failed batch for FileID: {file_id_db}")
    background_tasks.add_task(run_job_with_logging, process_restart_batch, file_id_db, file_id=file_id_db)
    return {"message": f"Processing restart initiated for FileID: {file_id_db}"}

@app.post("/process-image-batch/")
async def api_process_payload(background_tasks: BackgroundTasks, payload: dict):
    file_id = payload.get('file_id', str(uuid.uuid4()))
    logger, _ = setup_job_logger(job_id=file_id)
    logger.info(f"Received request to process image batch for FileID: {file_id}")
    try:
        background_tasks.add_task(run_job_with_logging, process_image_batch, payload, file_id=file_id)
        return {"message": "Processing started successfully"}
    except Exception as e:
        logger.error(f"Error processing payload: {e}")
        return {"error": f"An error occurred: {str(e)}"}

@app.post("/generate-download-file/")
async def api_generate_download_file(background_tasks: BackgroundTasks, file_id: int):
    file_id_str = str(file_id)
    logger, _ = setup_job_logger(job_id=file_id_str)
    logger.info(f"Received request to generate download file for FileID: {file_id}")
    try:
        background_tasks.add_task(run_job_with_logging, generate_download_file, file_id_str, file_id=file_id_str)
        return {"message": "Processing started successfully"}
    except Exception as e:
        logger.error(f"Error generating download file: {e}")
        return {"error": f"An error occurred: {str(e)}"}