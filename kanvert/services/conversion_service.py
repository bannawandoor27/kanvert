"""
Conversion service for handling document conversions.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..core.models import ConversionOptions
from ..core.database import get_database

logger = logging.getLogger(__name__)


class ConversionService:
    """Service for managing document conversions."""
    
    def __init__(self):
        pass
    
    async def convert_file(
        self,
        file_path: str,
        output_path: str,
        options: ConversionOptions
    ) -> Dict[str, Any]:
        """Convert a single file."""
        try:
            # This is a placeholder implementation
            # In a real implementation, this would use the converter registry
            logger.info(f"Converting {file_path} to {output_path}")
            
            # Simulate conversion process
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "output_path": output_path,
                "processing_time": 1.0,
                "file_size": 1024
            }
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_batch_job(self, job_id: str, user_id: str) -> None:
        """Process all files in a batch job."""
        db = await get_database()
        
        try:
            # Get job details
            job = await db.batch_jobs.find_one({
                "_id": job_id,
                "user_id": user_id
            })
            
            if not job:
                return
            
            files = job.get("files", [])
            options = ConversionOptions(**job.get("options", {}))
            
            total_files = len(files)
            completed = 0
            
            for file_info in files:
                # Update file status to processing
                await db.batch_jobs.update_one(
                    {"_id": job_id, "files.id": file_info["id"]},
                    {"$set": {"files.$.status": "processing", "files.$.progress": 0}}
                )
                
                # Convert file
                result = await self.convert_file(
                    file_info["file_path"],
                    f"output/{file_info['id']}.pdf",
                    options
                )
                
                if result["success"]:
                    # Update file as completed
                    await db.batch_jobs.update_one(
                        {"_id": job_id, "files.id": file_info["id"]},
                        {
                            "$set": {
                                "files.$.status": "completed",
                                "files.$.progress": 100,
                                "files.$.result_url": f"/download/{file_info['id']}.pdf"
                            }
                        }
                    )
                    completed += 1
                else:
                    # Update file as failed
                    await db.batch_jobs.update_one(
                        {"_id": job_id, "files.id": file_info["id"]},
                        {
                            "$set": {
                                "files.$.status": "failed",
                                "files.$.progress": 0,
                                "files.$.error": result["error"]
                            }
                        }
                    )
                
                # Update overall job progress
                progress = int((completed / total_files) * 100)
                await db.batch_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"progress": progress}}
                )
            
            # Mark job as completed
            status = "completed" if completed == total_files else "failed"
            await db.batch_jobs.update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "status": status,
                        "completed_at": datetime.utcnow(),
                        "progress": 100
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Batch job {job_id} failed: {e}")
            await db.batch_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "failed", "error": str(e)}}
            )
    
    async def apply_template(self, template_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Apply a conversion template to get options."""
        db = await get_database()
        
        template = await db.conversion_templates.find_one({
            "_id": template_id,
            "user_id": user_id
        })
        
        if template:
            # Increment usage count
            await db.conversion_templates.update_one(
                {"_id": template_id},
                {"$inc": {"usage_count": 1}}
            )
            
            return template.get("options", {})
        
        return None
    
    async def create_template_from_job(
        self, 
        job_id: str, 
        user_id: str, 
        template_name: str,
        description: str
    ) -> Optional[str]:
        """Create a template from an existing batch job."""
        db = await get_database()
        
        job = await db.batch_jobs.find_one({
            "_id": job_id,
            "user_id": user_id
        })
        
        if not job:
            return None
        
        template_id = f"tpl_{job_id}_{template_name.lower().replace(' ', '_')}"
        
        template = {
            "_id": template_id,
            "user_id": user_id,
            "name": template_name,
            "description": description,
            "input_format": "auto",
            "output_format": "pdf",
            "options": job.get("options", {}),
            "created_at": datetime.utcnow(),
            "usage_count": 0,
            "is_default": False
        }
        
        await db.conversion_templates.insert_one(template)
        return template_id