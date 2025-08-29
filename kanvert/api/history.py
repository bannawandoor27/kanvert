"""
Conversion History API endpoints.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from enum import Enum
from ..core.database import get_database
from ..core.models import User, ConversionStatus
from ..api.auth import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SortField(str, Enum):
    created_at = "created_at"
    file_name = "file_name"
    file_size = "file_size"
    processing_time = "processing_time"
    status = "status"


class ConversionHistoryItem(BaseModel):
    id: str
    job_id: str
    input_format: str
    output_format: str
    input_filename: str
    output_filename: Optional[str]
    file_size: int
    status: ConversionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversionHistoryResponse(BaseModel):
    items: List[ConversionHistoryItem]
    total: int
    page: int
    per_page: int
    total_pages: int


class BulkActionRequest(BaseModel):
    action: str  # 'download', 'archive', 'delete'
    conversion_ids: List[str]


class ConversionFilters(BaseModel):
    status: Optional[ConversionStatus] = None
    format: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    if bytes_value == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


@router.get("/", response_model=ConversionHistoryResponse)
async def get_conversion_history(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[ConversionStatus] = Query(None),
    format: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_field: SortField = Query(SortField.created_at),
    sort_order: SortOrder = Query(SortOrder.desc)
):
    """Get conversion history with filtering, search, and pagination."""
    db = await get_database()
    
    # Build query filter
    query_filter = {"user_id": current_user.id}
    
    # Add status filter
    if status:
        query_filter["status"] = status
    
    # Add format filter
    if format:
        query_filter["$or"] = [
            {"input_format": {"$regex": format, "$options": "i"}},
            {"output_format": {"$regex": format, "$options": "i"}}
        ]
    
    # Add date range filter
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query_filter["created_at"] = date_filter
    
    # Add search filter
    if search:
        search_filter = {
            "$or": [
                {"input_filename": {"$regex": search, "$options": "i"}},
                {"output_filename": {"$regex": search, "$options": "i"}},
                {"job_id": {"$regex": search, "$options": "i"}}
            ]
        }
        if "$or" in query_filter:
            # Combine with existing $or
            query_filter = {
                "$and": [
                    {"user_id": current_user.id},
                    query_filter,
                    search_filter
                ]
            }
        else:
            query_filter.update(search_filter)
    
    # Get total count
    total = await db.conversions.count_documents(query_filter)
    
    # Calculate pagination
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page
    
    # Build sort criteria
    sort_direction = 1 if sort_order == SortOrder.asc else -1
    sort_criteria = [(sort_field.value, sort_direction)]
    
    # Get paginated results
    conversions = await db.conversions.find(query_filter).sort(sort_criteria).skip(skip).limit(per_page).to_list(per_page)
    
    # Convert to response format
    items = []
    for conv in conversions:
        items.append(ConversionHistoryItem(
            id=str(conv["_id"]),
            job_id=conv.get("job_id", str(conv["_id"])),
            input_format=conv.get("input_format", "unknown"),
            output_format=conv.get("output_format", "PDF"),
            input_filename=conv.get("input_filename", "unknown"),
            output_filename=conv.get("output_filename"),
            file_size=conv.get("file_size", 0),
            status=conv["status"],
            created_at=conv["created_at"],
            completed_at=conv.get("completed_at"),
            processing_time=conv.get("processing_time"),
            download_url=conv.get("download_url"),
            error_message=conv.get("error_message"),
            metadata=conv.get("metadata", {})
        ))
    
    return ConversionHistoryResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{conversion_id}", response_model=ConversionHistoryItem)
async def get_conversion_details(
    conversion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific conversion."""
    db = await get_database()
    
    # Find conversion by ID and ensure it belongs to the user
    conversion = await db.conversions.find_one({
        "_id": conversion_id,
        "user_id": current_user.id
    })
    
    if not conversion:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    return ConversionHistoryItem(
        id=str(conversion["_id"]),
        job_id=conversion.get("job_id", str(conversion["_id"])),
        input_format=conversion.get("input_format", "unknown"),
        output_format=conversion.get("output_format", "PDF"),
        input_filename=conversion.get("input_filename", "unknown"),
        output_filename=conversion.get("output_filename"),
        file_size=conversion.get("file_size", 0),
        status=conversion["status"],
        created_at=conversion["created_at"],
        completed_at=conversion.get("completed_at"),
        processing_time=conversion.get("processing_time"),
        download_url=conversion.get("download_url"),
        error_message=conversion.get("error_message"),
        metadata=conversion.get("metadata", {})
    )


@router.delete("/{conversion_id}")
async def delete_conversion(
    conversion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a specific conversion from history."""
    db = await get_database()
    
    # Find and delete conversion
    result = await db.conversions.delete_one({
        "_id": conversion_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversion not found")
    
    # TODO: Also delete associated files from storage
    
    return {"message": "Conversion deleted successfully"}


@router.post("/bulk-action")
async def bulk_action(
    request: BulkActionRequest,
    current_user: User = Depends(get_current_user)
):
    """Perform bulk actions on multiple conversions."""
    db = await get_database()
    
    if not request.conversion_ids:
        raise HTTPException(status_code=400, detail="No conversion IDs provided")
    
    # Verify all conversions belong to the user
    conversions = await db.conversions.find({
        "_id": {"$in": request.conversion_ids},
        "user_id": current_user.id
    }).to_list(len(request.conversion_ids))
    
    found_ids = [str(conv["_id"]) for conv in conversions]
    missing_ids = [id for id in request.conversion_ids if id not in found_ids]
    
    if missing_ids:
        raise HTTPException(
            status_code=404, 
            detail=f"Conversions not found: {missing_ids}"
        )
    
    result = {"processed": 0, "failed": 0, "errors": []}
    
    if request.action == "delete":
        # Delete multiple conversions
        delete_result = await db.conversions.delete_many({
            "_id": {"$in": request.conversion_ids},
            "user_id": current_user.id
        })
        result["processed"] = delete_result.deleted_count
        
        # TODO: Delete associated files from storage
        
    elif request.action == "archive":
        # Mark conversions as archived
        update_result = await db.conversions.update_many(
            {
                "_id": {"$in": request.conversion_ids},
                "user_id": current_user.id
            },
            {"$set": {"archived": True, "archived_at": datetime.utcnow()}}
        )
        result["processed"] = update_result.modified_count
        
    elif request.action == "download":
        # Generate bulk download links
        download_urls = []
        for conversion in conversions:
            if conversion.get("download_url") and conversion["status"] == "completed":
                download_urls.append({
                    "id": str(conversion["_id"]),
                    "filename": conversion.get("output_filename", "converted_file"),
                    "url": conversion["download_url"]
                })
                result["processed"] += 1
            else:
                result["failed"] += 1
                result["errors"].append(f"No download available for {conversion['_id']}")
        
        result["download_urls"] = download_urls
        
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
    
    return result


@router.get("/stats/summary")
async def get_history_stats(
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365)
):
    """Get conversion history statistics summary."""
    db = await get_database()
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get basic statistics
    pipeline = [
        {
            "$match": {
                "user_id": current_user.id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_conversions": {"$sum": 1},
                "successful_conversions": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                },
                "failed_conversions": {
                    "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                },
                "total_file_size": {"$sum": "$file_size"},
                "avg_processing_time": {"$avg": "$processing_time"},
                "total_processing_time": {"$sum": "$processing_time"}
            }
        }
    ]
    
    stats = await db.conversions.aggregate(pipeline).to_list(1)
    
    if not stats:
        return {
            "period_days": days,
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "success_rate": 0,
            "total_file_size": 0,
            "avg_processing_time": 0,
            "total_processing_time": 0,
            "most_popular_format": None
        }
    
    stat = stats[0]
    
    # Get most popular conversion format
    format_pipeline = [
        {
            "$match": {
                "user_id": current_user.id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": "$output_format",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    
    format_stats = await db.conversions.aggregate(format_pipeline).to_list(1)
    most_popular_format = format_stats[0]["_id"] if format_stats else None
    
    success_rate = (stat["successful_conversions"] / stat["total_conversions"] * 100) if stat["total_conversions"] > 0 else 0
    
    return {
        "period_days": days,
        "total_conversions": stat["total_conversions"],
        "successful_conversions": stat["successful_conversions"],
        "failed_conversions": stat["failed_conversions"],
        "success_rate": round(success_rate, 2),
        "total_file_size": stat["total_file_size"],
        "total_file_size_formatted": format_bytes(stat["total_file_size"]),
        "avg_processing_time": round(stat["avg_processing_time"] or 0, 2),
        "total_processing_time": round(stat["total_processing_time"] or 0, 2),
        "most_popular_format": most_popular_format
    }


@router.get("/stats/daily")
async def get_daily_stats(
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365)
):
    """Get daily conversion statistics."""
    db = await get_database()
    
    # Calculate date range
    end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
    start_date = end_date - timedelta(days=days - 1)
    start_date = start_date.replace(hour=0, minute=0, second=0)
    
    # Aggregate daily statistics
    pipeline = [
        {
            "$match": {
                "user_id": current_user.id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "conversions": {"$sum": 1},
                "successful": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                },
                "failed": {
                    "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                },
                "total_size": {"$sum": "$file_size"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_stats = await db.conversions.aggregate(pipeline).to_list(days)
    
    # Fill in missing dates with zero values
    result = []
    current_date = start_date.date()
    
    for i in range(days):
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Find stats for this date
        day_stats = next((stat for stat in daily_stats if stat["_id"] == date_str), None)
        
        if day_stats:
            result.append({
                "date": date_str,
                "conversions": day_stats["conversions"],
                "successful": day_stats["successful"],
                "failed": day_stats["failed"],
                "success_rate": (day_stats["successful"] / day_stats["conversions"] * 100) if day_stats["conversions"] > 0 else 0,
                "total_size": day_stats["total_size"]
            })
        else:
            result.append({
                "date": date_str,
                "conversions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0,
                "total_size": 0
            })
        
        current_date += timedelta(days=1)
    
    return {"daily_stats": result}


@router.post("/export")
async def export_history(
    current_user: User = Depends(get_current_user),
    filters: ConversionFilters = None,
    format: str = Query("csv", regex="^(csv|json)$")
):
    """Export conversion history data."""
    db = await get_database()
    
    # Build query filter
    query_filter = {"user_id": current_user.id}
    
    if filters:
        if filters.status:
            query_filter["status"] = filters.status
        if filters.format:
            query_filter["$or"] = [
                {"input_format": {"$regex": filters.format, "$options": "i"}},
                {"output_format": {"$regex": filters.format, "$options": "i"}}
            ]
        if filters.start_date or filters.end_date:
            date_filter = {}
            if filters.start_date:
                date_filter["$gte"] = filters.start_date
            if filters.end_date:
                date_filter["$lte"] = filters.end_date
            query_filter["created_at"] = date_filter
    
    # Get all matching conversions
    conversions = await db.conversions.find(query_filter).sort("created_at", -1).to_list(None)
    
    if format == "csv":
        # Generate CSV export
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Job ID", "Input Format", "Output Format", "Filename",
            "File Size", "Status", "Created At", "Completed At", "Processing Time (s)"
        ])
        
        # Write data
        for conv in conversions:
            writer.writerow([
                str(conv["_id"]),
                conv.get("job_id", ""),
                conv.get("input_format", ""),
                conv.get("output_format", ""),
                conv.get("input_filename", ""),
                conv.get("file_size", 0),
                conv["status"],
                conv["created_at"].isoformat(),
                conv.get("completed_at", "").isoformat() if conv.get("completed_at") else "",
                conv.get("processing_time", "")
            ])
        
        return {
            "format": "csv",
            "content": output.getvalue(),
            "filename": f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    
    else:  # JSON format
        export_data = []
        for conv in conversions:
            export_data.append({
                "id": str(conv["_id"]),
                "job_id": conv.get("job_id"),
                "input_format": conv.get("input_format"),
                "output_format": conv.get("output_format"),
                "input_filename": conv.get("input_filename"),
                "output_filename": conv.get("output_filename"),
                "file_size": conv.get("file_size"),
                "status": conv["status"],
                "created_at": conv["created_at"].isoformat(),
                "completed_at": conv.get("completed_at").isoformat() if conv.get("completed_at") else None,
                "processing_time": conv.get("processing_time"),
                "error_message": conv.get("error_message"),
                "metadata": conv.get("metadata")
            })
        
        return {
            "format": "json",
            "content": export_data,
            "filename": f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }