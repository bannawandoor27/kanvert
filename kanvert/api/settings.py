"""
User Settings and Preferences API endpoints.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
import secrets
from ..core.database import get_database
from ..core.models import User, SubscriptionTier
from ..api.auth import get_current_user, get_password_hash

router = APIRouter(prefix="/settings", tags=["settings"])


class UserProfile(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    country: str = "US"


class NotificationSettings(BaseModel):
    email: bool = True
    browser: bool = True
    conversion_complete: bool = True
    conversion_failed: bool = True
    weekly_reports: bool = True
    product_updates: bool = True
    marketing: bool = False


class ConversionDefaults(BaseModel):
    default_output_format: str = "PDF"
    auto_download: bool = True
    delete_after_download: bool = False
    compression_level: str = "medium"
    quality_setting: str = "high"
    watermark_enabled: bool = False
    watermark_text: Optional[str] = None


class APIKeyInfo(BaseModel):
    id: str
    name: str
    key_preview: str  # First 8 chars + "..."
    created_at: datetime
    last_used: Optional[datetime] = None
    permissions: list[str]
    is_active: bool = True


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class APIKeyCreateRequest(BaseModel):
    name: str
    permissions: list[str]


class UserSettings(BaseModel):
    profile: UserProfile
    notifications: NotificationSettings
    conversion_defaults: ConversionDefaults
    subscription: SubscriptionTier
    api_keys: list[APIKeyInfo]
    usage_stats: Dict[str, Any]


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user profile information."""
    db = await get_database()
    
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        email=user["email"],
        company=user.get("company"),
        job_title=user.get("job_title"),
        phone=user.get("phone"),
        timezone=user.get("timezone", "UTC"),
        language=user.get("language", "en"),
        country=user.get("country", "US")
    )


@router.put("/profile")
async def update_user_profile(
    profile: UserProfile,
    current_user: User = Depends(get_current_user)
):
    """Update user profile information."""
    db = await get_database()
    
    # Check if email is being changed and if it's already in use
    if profile.email != current_user.email:
        existing_user = await db.users.find_one({"email": profile.email})
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already in use")
    
    update_data = profile.dict()
    update_data["name"] = f"{profile.first_name} {profile.last_name}"
    
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    return {"message": "Profile updated successfully"}


@router.get("/notifications", response_model=NotificationSettings)
async def get_notification_settings(current_user: User = Depends(get_current_user)):
    """Get user notification settings."""
    db = await get_database()
    
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = user.get("preferences", {}).get("notifications", {})
    
    return NotificationSettings(
        email=notifications.get("email", True),
        browser=notifications.get("browser", True),
        conversion_complete=notifications.get("conversion_complete", True),
        conversion_failed=notifications.get("conversion_failed", True),
        weekly_reports=notifications.get("weekly_reports", True),
        product_updates=notifications.get("product_updates", True),
        marketing=notifications.get("marketing", False)
    )


@router.put("/notifications")
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: User = Depends(get_current_user)
):
    """Update user notification settings."""
    db = await get_database()
    
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"preferences.notifications": settings.dict()}}
    )
    
    return {"message": "Notification settings updated successfully"}


@router.get("/conversion-defaults", response_model=ConversionDefaults)
async def get_conversion_defaults(current_user: User = Depends(get_current_user)):
    """Get user conversion default settings."""
    db = await get_database()
    
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    defaults = user.get("preferences", {}).get("conversion_defaults", {})
    
    return ConversionDefaults(
        default_output_format=defaults.get("default_output_format", "PDF"),
        auto_download=defaults.get("auto_download", True),
        delete_after_download=defaults.get("delete_after_download", False),
        compression_level=defaults.get("compression_level", "medium"),
        quality_setting=defaults.get("quality_setting", "high"),
        watermark_enabled=defaults.get("watermark_enabled", False),
        watermark_text=defaults.get("watermark_text")
    )


@router.put("/conversion-defaults")
async def update_conversion_defaults(
    defaults: ConversionDefaults,
    current_user: User = Depends(get_current_user)
):
    """Update user conversion default settings."""
    db = await get_database()
    
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"preferences.conversion_defaults": defaults.dict()}}
    )
    
    return {"message": "Conversion defaults updated successfully"}


@router.post("/password-change")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """Change user password."""
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    
    db = await get_database()
    
    # Verify current password
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from ..api.auth import verify_password
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    new_password_hash = get_password_hash(request.new_password)
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    return {"message": "Password changed successfully"}


@router.get("/api-keys", response_model=list[APIKeyInfo])
async def get_api_keys(current_user: User = Depends(get_current_user)):
    """Get user's API keys."""
    db = await get_database()
    
    api_keys = await db.api_keys.find({
        "user_id": current_user.id,
        "is_active": True
    }).sort("created_at", -1).to_list(10)
    
    return [
        APIKeyInfo(
            id=str(key["_id"]),
            name=key["name"],
            key_preview=f"{key['key'][:8]}...",
            created_at=key["created_at"],
            last_used=key.get("last_used"),
            permissions=key["permissions"],
            is_active=key["is_active"]
        )
        for key in api_keys
    ]


@router.post("/api-keys", response_model=dict)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new API key."""
    db = await get_database()
    
    # Check API key limit based on subscription
    key_limits = {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PROFESSIONAL: 5,
        SubscriptionTier.ENTERPRISE: 20
    }
    
    current_count = await db.api_keys.count_documents({
        "user_id": current_user.id,
        "is_active": True
    })
    
    limit = key_limits.get(current_user.subscription, 1)
    if current_count >= limit:
        raise HTTPException(
            status_code=400,
            detail=f"API key limit reached for {current_user.subscription} plan ({limit} keys)"
        )
    
    # Generate new API key
    api_key = f"kv_{secrets.token_urlsafe(32)}"
    key_id = secrets.token_urlsafe(16)
    
    key_data = {
        "_id": key_id,
        "user_id": current_user.id,
        "name": request.name,
        "key": api_key,
        "permissions": request.permissions,
        "created_at": datetime.utcnow(),
        "last_used": None,
        "is_active": True
    }
    
    await db.api_keys.insert_one(key_data)
    
    return {
        "message": "API key created successfully",
        "key_id": key_id,
        "api_key": api_key,  # Only returned on creation
        "name": request.name
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Revoke an API key."""
    db = await get_database()
    
    result = await db.api_keys.update_one(
        {
            "_id": key_id,
            "user_id": current_user.id
        },
        {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {"message": "API key revoked successfully"}


@router.get("/usage-stats")
async def get_usage_statistics(current_user: User = Depends(get_current_user)):
    """Get user usage statistics."""
    db = await get_database()
    
    # Get conversion statistics
    total_conversions = await db.conversions.count_documents({
        "user_id": current_user.id
    })
    
    successful_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "status": "completed"
    })
    
    failed_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "status": "failed"
    })
    
    # Get monthly usage
    from datetime import datetime, timedelta
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_conversions = await db.conversions.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": month_start}
    })
    
    # Get file size statistics
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": None,
            "total_size": {"$sum": "$file_size"},
            "avg_size": {"$avg": "$file_size"}
        }}
    ]
    
    size_stats = await db.conversions.aggregate(pipeline).to_list(1)
    total_size = size_stats[0]["total_size"] if size_stats else 0
    avg_size = size_stats[0]["avg_size"] if size_stats else 0
    
    # Get subscription limits
    subscription_limits = {
        SubscriptionTier.FREE: {
            "conversions_per_month": 100,
            "max_file_size": 5 * 1024 * 1024,  # 5MB
            "api_calls_per_hour": 50
        },
        SubscriptionTier.PROFESSIONAL: {
            "conversions_per_month": 1000,
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "api_calls_per_hour": 1000
        },
        SubscriptionTier.ENTERPRISE: {
            "conversions_per_month": -1,  # Unlimited
            "max_file_size": 200 * 1024 * 1024,  # 200MB
            "api_calls_per_hour": 10000
        }
    }
    
    limits = subscription_limits.get(current_user.subscription, subscription_limits[SubscriptionTier.FREE])
    
    return {
        "total_conversions": total_conversions,
        "successful_conversions": successful_conversions,
        "failed_conversions": failed_conversions,
        "success_rate": (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0,
        "monthly_conversions": monthly_conversions,
        "monthly_limit": limits["conversions_per_month"],
        "monthly_usage_percentage": (monthly_conversions / limits["conversions_per_month"] * 100) if limits["conversions_per_month"] > 0 else 0,
        "total_file_size_bytes": total_size,
        "average_file_size_bytes": avg_size,
        "subscription": current_user.subscription,
        "limits": limits
    }


@router.get("/", response_model=UserSettings)
async def get_all_settings(current_user: User = Depends(get_current_user)):
    """Get all user settings in one request."""
    db = await get_database()
    
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get profile
    profile = UserProfile(
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        email=user["email"],
        company=user.get("company"),
        job_title=user.get("job_title"),
        phone=user.get("phone"),
        timezone=user.get("timezone", "UTC"),
        language=user.get("language", "en"),
        country=user.get("country", "US")
    )
    
    # Get notification settings
    notifications_data = user.get("preferences", {}).get("notifications", {})
    notifications = NotificationSettings(
        email=notifications_data.get("email", True),
        browser=notifications_data.get("browser", True),
        conversion_complete=notifications_data.get("conversion_complete", True),
        conversion_failed=notifications_data.get("conversion_failed", True),
        weekly_reports=notifications_data.get("weekly_reports", True),
        product_updates=notifications_data.get("product_updates", True),
        marketing=notifications_data.get("marketing", False)
    )
    
    # Get conversion defaults
    defaults_data = user.get("preferences", {}).get("conversion_defaults", {})
    conversion_defaults = ConversionDefaults(
        default_output_format=defaults_data.get("default_output_format", "PDF"),
        auto_download=defaults_data.get("auto_download", True),
        delete_after_download=defaults_data.get("delete_after_download", False),
        compression_level=defaults_data.get("compression_level", "medium"),
        quality_setting=defaults_data.get("quality_setting", "high"),
        watermark_enabled=defaults_data.get("watermark_enabled", False),
        watermark_text=defaults_data.get("watermark_text")
    )
    
    # Get API keys
    api_keys_data = await db.api_keys.find({
        "user_id": current_user.id,
        "is_active": True
    }).sort("created_at", -1).to_list(10)
    
    api_keys = [
        APIKeyInfo(
            id=str(key["_id"]),
            name=key["name"],
            key_preview=f"{key['key'][:8]}...",
            created_at=key["created_at"],
            last_used=key.get("last_used"),
            permissions=key["permissions"],
            is_active=key["is_active"]
        )
        for key in api_keys_data
    ]
    
    # Get usage stats
    usage_stats = await get_usage_statistics(current_user)
    
    return UserSettings(
        profile=profile,
        notifications=notifications,
        conversion_defaults=conversion_defaults,
        subscription=current_user.subscription,
        api_keys=api_keys,
        usage_stats=usage_stats
    )