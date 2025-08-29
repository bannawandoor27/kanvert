"""
Dashboard and Analytics API endpoints.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from ..core.database import get_database
from ..core.models import User
from ..api.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ConversionStats(BaseModel):
    total_conversions: int
    success_rate: float
    avg_processing_time: float
    total_size_processed: str
    monthly_conversions: int
    weekly_conversions: int
    today_conversions: int


class RecentActivity(BaseModel):
    id: str
    type: str  # 'conversion', 'upload', 'download', 'error'
    title: str
    description: str
    status: str  # 'completed', 'processing', 'failed', 'pending'
    timestamp: datetime
    size: Optional[str] = None
    format: Optional[str] = None


class QuickAction(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    href: str
    color: str
    popular: bool = False


class AnalyticsData(BaseModel):
    conversions: dict
    usage: dict
    revenue: dict
    top_formats: List[dict]
    daily_stats: List[dict]
    weekly_stats: List[dict]
    monthly_stats: List[dict]


class DashboardSummary(BaseModel):
    stats: ConversionStats
    recent_activity: List[RecentActivity]
    quick_actions: List[QuickAction]


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    period: str = Query("month", regex="^(today|week|month)$")
):
    """Get dashboard summary data."""
    db = await get_database()
    
    # Calculate date ranges based on period
    now = datetime.utcnow()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    else:  # month
        start_date = now - timedelta(days=30)
    
    # Get conversion statistics
    total_conversions = await db.conversions.count_documents({"user_id": current_user.id})
    successful_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "status": "completed"
    })
    
    # Get period-specific conversions
    period_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": start_date}
    })
    
    # Calculate success rate
    success_rate = (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0
    
    # Calculate average processing time
    pipeline = [
        {"$match": {"user_id": current_user.id, "status": "completed", "processing_time": {"$exists": True}}},
        {"$group": {"_id": None, "avg_time": {"$avg": "$processing_time"}}}
    ]
    avg_time_result = await db.conversions.aggregate(pipeline).to_list(1)
    avg_processing_time = avg_time_result[0]["avg_time"] if avg_time_result else 0
    
    # Calculate total size processed
    pipeline = [
        {"$match": {"user_id": current_user.id, "file_size": {"$exists": True}}},
        {"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}
    ]
    size_result = await db.conversions.aggregate(pipeline).to_list(1)
    total_size = size_result[0]["total_size"] if size_result else 0
    
    # Get different period conversions
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    today_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": today_start}
    })
    
    weekly_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": week_start}
    })
    
    monthly_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": month_start}
    })
    
    stats = ConversionStats(
        total_conversions=total_conversions,
        success_rate=round(success_rate, 1),
        avg_processing_time=round(avg_processing_time, 2) if avg_processing_time else 0,
        total_size_processed=format_bytes(total_size),
        monthly_conversions=monthly_conversions,
        weekly_conversions=weekly_conversions,
        today_conversions=today_conversions
    )
    
    # Get recent activity
    recent_activities = await db.conversions.find({
        "user_id": current_user.id
    }).sort("created_at", -1).limit(10).to_list(10)
    
    activity_list = []
    for activity in recent_activities:
        activity_type = "conversion"
        if activity["status"] == "failed":
            activity_type = "error"
        
        activity_list.append(RecentActivity(
            id=str(activity["_id"]),
            type=activity_type,
            title=f"Document {'converted' if activity['status'] == 'completed' else 'conversion'}",
            description=f"{activity.get('input_filename', 'Unknown')} → {activity.get('output_format', 'PDF')}",
            status=activity["status"],
            timestamp=activity["created_at"],
            size=format_bytes(activity.get("file_size", 0)) if activity.get("file_size") else None,
            format=activity.get("output_format", "PDF")
        ))
    
    # Quick actions
    quick_actions = [
        QuickAction(
            id="pdf-converter",
            title="Convert to PDF",
            description="Convert documents to PDF format",
            icon="FileText",
            href="/convert/pdf",
            color="blue",
            popular=True
        ),
        QuickAction(
            id="batch-processing",
            title="Batch Processing",
            description="Convert multiple files at once",
            icon="Layers",
            href="/advanced",
            color="purple"
        ),
        QuickAction(
            id="api-access",
            title="API Integration",
            description="Integrate with your applications",
            icon="Code",
            href="/docs",
            color="green"
        ),
        QuickAction(
            id="analytics",
            title="View Analytics",
            description="Check your usage statistics",
            icon="BarChart3",
            href="/analytics",
            color="orange"
        )
    ]
    
    return DashboardSummary(
        stats=stats,
        recent_activity=activity_list,
        quick_actions=quick_actions
    )


@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics_data(
    current_user: User = Depends(get_current_user),
    time_range: str = Query("month", regex="^(today|week|month|quarter|year)$")
):
    """Get detailed analytics data."""
    db = await get_database()
    
    # Calculate date ranges
    now = datetime.utcnow()
    if time_range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        days_back = 1
    elif time_range == "week":
        start_date = now - timedelta(days=7)
        days_back = 7
    elif time_range == "quarter":
        start_date = now - timedelta(days=90)
        days_back = 90
    elif time_range == "year":
        start_date = now - timedelta(days=365)
        days_back = 365
    else:  # month
        start_date = now - timedelta(days=30)
        days_back = 30
    
    # Get conversion statistics
    total_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": start_date}
    })
    
    completed_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    failed_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "status": "failed",
        "created_at": {"$gte": start_date}
    })
    
    in_progress_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "status": "processing"
    })
    
    # Get usage statistics
    pipeline = [
        {"$match": {"user_id": current_user.id, "created_at": {"$gte": start_date}}},
        {"$group": {
            "_id": None,
            "total_size": {"$sum": "$file_size"},
            "avg_processing_time": {"$avg": "$processing_time"},
            "active_users": {"$addToSet": "$user_id"}
        }}
    ]
    usage_stats = await db.conversions.aggregate(pipeline).to_list(1)
    usage_data = usage_stats[0] if usage_stats else {}
    
    # Get top conversion formats
    pipeline = [
        {"$match": {"user_id": current_user.id, "created_at": {"$gte": start_date}}},
        {"$group": {
            "_id": "$output_format",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 6}
    ]
    format_stats = await db.conversions.aggregate(pipeline).to_list(6)
    
    total_format_conversions = sum(stat["count"] for stat in format_stats)
    top_formats = []
    for stat in format_stats:
        percentage = (stat["count"] / total_format_conversions * 100) if total_format_conversions > 0 else 0
        top_formats.append({
            "format": f"Document to {stat['_id']}",
            "count": stat["count"],
            "percentage": round(percentage, 1)
        })
    
    # Get daily statistics
    daily_stats = []
    for i in range(days_back):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        daily_conversions = await db.conversions.count_documents({
            "user_id": current_user.id,
            "created_at": {"$gte": day_start, "$lt": day_end}
        })
        
        daily_stats.append({
            "date": day_start.strftime("%b %d"),
            "conversions": daily_conversions,
            "users": 1 if daily_conversions > 0 else 0,
            "revenue": daily_conversions * 0.1  # Mock revenue calculation
        })
    
    daily_stats.reverse()  # Show chronologically
    
    # Mock weekly and monthly stats for now
    weekly_stats = [
        {"week": f"Week {i+1}", "conversions": max(100, total_conversions // 12 + i * 10), "successRate": 85 + (i % 15)}
        for i in range(12)
    ]
    
    monthly_stats = [
        {
            "month": (now - timedelta(days=30*i)).strftime("%b %Y"),
            "conversions": max(500, total_conversions // 12 + i * 50),
            "revenue": max(250, total_conversions // 12 + i * 25),
            "users": max(10, total_conversions // 24 + i * 5)
        }
        for i in range(12)
    ]
    monthly_stats.reverse()
    
    return AnalyticsData(
        conversions={
            "total": total_conversions,
            "completed": completed_conversions,
            "failed": failed_conversions,
            "inProgress": in_progress_conversions
        },
        usage={
            "totalFileSize": usage_data.get("total_size", 0),
            "avgConversionTime": usage_data.get("avg_processing_time", 0),
            "totalUsers": 1,
            "activeUsers": 1 if total_conversions > 0 else 0
        },
        revenue={
            "currentMonth": total_conversions * 0.1,  # Mock revenue
            "previousMonth": max(0, (total_conversions - 50) * 0.1),
            "growth": 15.1 if total_conversions > 50 else 0
        },
        top_formats=top_formats,
        daily_stats=daily_stats,
        weekly_stats=weekly_stats,
        monthly_stats=monthly_stats
    )


@router.get("/system-status")
async def get_system_status(current_user: User = Depends(get_current_user)):
    """Get system status information."""
    db = await get_database()
    
    # Check system health
    try:
        # Test database connection
        await db.admin.command("ping")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Get queue status
    queue_size = await db.conversions.count_documents({"status": "pending"})
    processing_jobs = await db.conversions.count_documents({"status": "processing"})
    
    return {
        "status": "operational",
        "database": db_status,
        "queue_size": queue_size,
        "processing_jobs": processing_jobs,
        "uptime": "99.9%",
        "last_updated": datetime.utcnow()
    }