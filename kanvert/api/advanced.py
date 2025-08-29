"""
Advanced conversion API endpoints for batch processing, templates, and scheduling.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import secrets
import json
import asyncio
from ..core.database import get_database
from ..core.models import User, ConversionOptions
from ..api.auth import get_current_user
from ..services.conversion_service import ConversionService

router = APIRouter(prefix="/advanced", tags=["advanced"])


class BatchFile(BaseModel):
    id: str
    name: str
    size: int
    type: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: int
    result_url: Optional[str] = None
    error: Optional[str] = None


class BatchJob(BaseModel):
    id: str
    name: str
    files: List[BatchFile]
    status: str  # 'pending', 'processing', 'completed', 'failed', 'paused'
    progress: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    options: Dict[str, Any]


class ConversionTemplate(BaseModel):
    id: str
    name: str
    description: str
    input_format: str
    output_format: str
    options: Dict[str, Any]
    created_at: datetime
    usage_count: int = 0
    is_default: bool = False


class ScheduledJob(BaseModel):
    id: str
    name: str
    template_id: str
    schedule_type: str  # 'once', 'daily', 'weekly', 'monthly'
    schedule_time: datetime
    next_run: datetime
    status: str  # 'active', 'paused', 'completed'
    created_at: datetime
    options: Dict[str, Any]


class BatchJobCreate(BaseModel):
    name: str
    options: ConversionOptions


class TemplateCreate(BaseModel):
    name: str
    description: str
    input_format: str
    output_format: str
    options: Dict[str, Any]


class ScheduledJobCreate(BaseModel):
    name: str
    template_id: str
    schedule_type: str
    schedule_time: datetime
    options: Dict[str, Any]


@router.post("/batch-jobs", response_model=BatchJob)
async def create_batch_job(
    job_data: BatchJobCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new batch conversion job."""
    db = await get_database()
    
    job_id = secrets.token_urlsafe(16)
    
    batch_job = {
        "_id": job_id,
        "user_id": current_user.id,
        "name": job_data.name,
        "files": [],
        "status": "pending",
        "progress": 0,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "options": job_data.options.dict()
    }
    
    await db.batch_jobs.insert_one(batch_job)
    
    return BatchJob(
        id=job_id,
        name=job_data.name,
        files=[],
        status="pending",
        progress=0,
        created_at=batch_job["created_at"],
        options=batch_job["options"]
    )


@router.post("/batch-jobs/{job_id}/files")
async def add_files_to_batch_job(
    job_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Add files to a batch job."""
    db = await get_database()
    
    # Verify job exists and belongs to user
    job = await db.batch_jobs.find_one({
        "_id": job_id,
        "user_id": current_user.id
    })
    
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    if job["status"] not in ["pending", "paused"]:
        raise HTTPException(status_code=400, detail="Cannot add files to a job in this status")
    
    batch_files = []
    for file in files:
        file_id = secrets.token_urlsafe(12)
        
        # Save file content
        content = await file.read()
        file_path = f"batch_files/{job_id}/{file_id}_{file.filename}"
        
        # Store file info in database
        file_info = {
            "id": file_id,
            "name": file.filename,
            "size": len(content),
            "type": file.content_type or "application/octet-stream",
            "status": "pending",
            "progress": 0,
            "file_path": file_path,
            "result_url": None,
            "error": None
        }
        
        batch_files.append(file_info)
    
    # Update job with new files
    await db.batch_jobs.update_one(
        {"_id": job_id},
        {"$push": {"files": {"$each": batch_files}}}
    )
    
    return {"message": f"Added {len(files)} files to batch job", "files": batch_files}


@router.post("/batch-jobs/{job_id}/start")
async def start_batch_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Start processing a batch job."""
    db = await get_database()
    
    # Verify job exists and belongs to user
    job = await db.batch_jobs.find_one({
        "_id": job_id,
        "user_id": current_user.id
    })
    
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    if job["status"] not in ["pending", "paused"]:
        raise HTTPException(status_code=400, detail="Job cannot be started in current status")
    
    if not job.get("files"):
        raise HTTPException(status_code=400, detail="No files in batch job")
    
    # Update job status to processing
    await db.batch_jobs.update_one(
        {"_id": job_id},
        {"$set": {"status": "processing"}}
    )
    
    # Start background processing
    asyncio.create_task(process_batch_job(job_id))
    
    return {"message": "Batch job started", "job_id": job_id}


async def process_batch_job(job_id: str):
    """Background task to process batch job files."""
    db = await get_database()
    conversion_service = ConversionService()
    
    job = await db.batch_jobs.find_one({"_id": job_id})
    if not job:
        return
    
    total_files = len(job["files"])
    completed_files = 0
    
    try:
        for i, file_info in enumerate(job["files"]):
            # Update file status to processing
            await db.batch_jobs.update_one(
                {"_id": job_id, "files.id": file_info["id"]},
                {"$set": {"files.$.status": "processing"}}
            )
            
            try:
                # Process the file
                # This would integrate with your existing conversion service
                result = await conversion_service.process_file(
                    file_info["file_path"],
                    job["options"]
                )
                
                # Update file as completed
                await db.batch_jobs.update_one(
                    {"_id": job_id, "files.id": file_info["id"]},
                    {"$set": {
                        "files.$.status": "completed",
                        "files.$.progress": 100,
                        "files.$.result_url": result.get("download_url")
                    }}
                )
                
                completed_files += 1
                
            except Exception as e:
                # Update file as failed
                await db.batch_jobs.update_one(
                    {"_id": job_id, "files.id": file_info["id"]},
                    {"$set": {
                        "files.$.status": "failed",
                        "files.$.error": str(e)
                    }}
                )
            
            # Update overall job progress
            progress = int((i + 1) / total_files * 100)
            await db.batch_jobs.update_one(
                {"_id": job_id},
                {"$set": {"progress": progress}}
            )
        
        # Mark job as completed
        await db.batch_jobs.update_one(
            {"_id": job_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "progress": 100
            }}
        )
        
    except Exception as e:
        # Mark job as failed
        await db.batch_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )


@router.get("/batch-jobs", response_model=List[BatchJob])
async def get_batch_jobs(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's batch jobs."""
    db = await get_database()
    
    jobs = await db.batch_jobs.find({
        "user_id": current_user.id
    }).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    return [
        BatchJob(
            id=job["_id"],
            name=job["name"],
            files=[BatchFile(**f) for f in job.get("files", [])],
            status=job["status"],
            progress=job.get("progress", 0),
            created_at=job["created_at"],
            completed_at=job.get("completed_at"),
            options=job["options"]
        )
        for job in jobs
    ]


@router.get("/batch-jobs/{job_id}", response_model=BatchJob)
async def get_batch_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific batch job."""
    db = await get_database()
    
    job = await db.batch_jobs.find_one({
        "_id": job_id,
        "user_id": current_user.id
    })
    
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    return BatchJob(
        id=job["_id"],
        name=job["name"],
        files=[BatchFile(**f) for f in job.get("files", [])],
        status=job["status"],
        progress=job.get("progress", 0),
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        options=job["options"]
    )


# Template Management
@router.post("/templates", response_model=ConversionTemplate)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new conversion template."""
    db = await get_database()
    
    template_id = secrets.token_urlsafe(16)
    
    template = {
        "_id": template_id,
        "user_id": current_user.id,
        "name": template_data.name,
        "description": template_data.description,
        "input_format": template_data.input_format,
        "output_format": template_data.output_format,
        "options": template_data.options,
        "created_at": datetime.utcnow(),
        "usage_count": 0,
        "is_default": False
    }
    
    await db.conversion_templates.insert_one(template)
    
    return ConversionTemplate(**template, id=template_id)


@router.get("/templates", response_model=List[ConversionTemplate])
async def get_templates(
    current_user: User = Depends(get_current_user)
):
    """Get user's conversion templates."""
    db = await get_database()
    
    # Get user templates and default system templates
    templates = await db.conversion_templates.find({
        "$or": [
            {"user_id": current_user.id},
            {"is_default": True}
        ]
    }).sort("created_at", -1).to_list(100)
    
    return [
        ConversionTemplate(
            id=template["_id"],
            name=template["name"],
            description=template["description"],
            input_format=template["input_format"],
            output_format=template["output_format"],
            options=template["options"],
            created_at=template["created_at"],
            usage_count=template.get("usage_count", 0),
            is_default=template.get("is_default", False)
        )
        for template in templates
    ]


@router.post("/templates/{template_id}/use")
async def use_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark template as used (increment usage count)."""
    db = await get_database()
    
    template = await db.conversion_templates.find_one({
        "_id": template_id,
        "$or": [
            {"user_id": current_user.id},
            {"is_default": True}
        ]
    })
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.conversion_templates.update_one(
        {"_id": template_id},
        {"$inc": {"usage_count": 1}}
    )
    
    return {"message": "Template usage recorded"}


# Scheduled Jobs
@router.post("/scheduled-jobs", response_model=ScheduledJob)
async def create_scheduled_job(
    job_data: ScheduledJobCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new scheduled conversion job."""
    db = await get_database()
    
    # Verify template exists
    template = await db.conversion_templates.find_one({
        "_id": job_data.template_id,
        "$or": [
            {"user_id": current_user.id},
            {"is_default": True}
        ]
    })
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    job_id = secrets.token_urlsafe(16)
    
    # Calculate next run time
    next_run = job_data.schedule_time
    if job_data.schedule_type == "daily":
        next_run = datetime.utcnow().replace(
            hour=job_data.schedule_time.hour,
            minute=job_data.schedule_time.minute,
            second=0,
            microsecond=0
        )
        if next_run <= datetime.utcnow():
            next_run += timedelta(days=1)
    
    scheduled_job = {
        "_id": job_id,
        "user_id": current_user.id,
        "name": job_data.name,
        "template_id": job_data.template_id,
        "schedule_type": job_data.schedule_type,
        "schedule_time": job_data.schedule_time,
        "next_run": next_run,
        "status": "active",
        "created_at": datetime.utcnow(),
        "options": job_data.options
    }
    
    await db.scheduled_jobs.insert_one(scheduled_job)
    
    return ScheduledJob(**scheduled_job, id=job_id)


@router.get("/scheduled-jobs", response_model=List[ScheduledJob])
async def get_scheduled_jobs(
    current_user: User = Depends(get_current_user)
):
    """Get user's scheduled jobs."""
    db = await get_database()
    
    jobs = await db.scheduled_jobs.find({
        "user_id": current_user.id
    }).sort("created_at", -1).to_list(100)
    
    return [
        ScheduledJob(
            id=job["_id"],
            name=job["name"],
            template_id=job["template_id"],
            schedule_type=job["schedule_type"],
            schedule_time=job["schedule_time"],
            next_run=job["next_run"],
            status=job["status"],
            created_at=job["created_at"],
            options=job["options"]
        )
        for job in jobs
    ]


@router.put("/scheduled-jobs/{job_id}/pause")
async def pause_scheduled_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Pause a scheduled job."""
    db = await get_database()
    
    result = await db.scheduled_jobs.update_one(
        {"_id": job_id, "user_id": current_user.id},
        {"$set": {"status": "paused"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    
    return {"message": "Scheduled job paused"}


@router.put("/scheduled-jobs/{job_id}/resume")
async def resume_scheduled_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume a paused scheduled job."""
    db = await get_database()
    
    result = await db.scheduled_jobs.update_one(
        {"_id": job_id, "user_id": current_user.id},
        {"$set": {"status": "active"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    
    return {"message": "Scheduled job resumed"}