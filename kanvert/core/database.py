"""
Database connection and initialization module using SQLite.
"""

import asyncio
import aiosqlite
import structlog
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..config.settings import get_settings

logger = structlog.get_logger(__name__)

# Global database connection
_database: Optional[aiosqlite.Connection] = None
_database_path: Optional[Path] = None


async def connect_to_database() -> aiosqlite.Connection:
    """Connect to SQLite database and create tables if needed."""
    global _database, _database_path
    
    if _database is not None:
        return _database
    
    settings = get_settings()
    
    try:
        # Set database path
        if hasattr(settings, 'DATABASE_PATH') and settings.DATABASE_PATH:
            _database_path = Path(settings.DATABASE_PATH)
        else:
            _database_path = Path("data/kanvert.db")
        
        # Create directory if it doesn't exist
        _database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to SQLite database
        _database = await aiosqlite.connect(str(_database_path))
        
        # Enable foreign keys
        await _database.execute("PRAGMA foreign_keys = ON")
        
        # Test connection
        await _database.execute("SELECT 1")
        logger.info(f"Connected to SQLite database: {_database_path}")
        
        # Create tables
        await create_tables()
        
        return _database
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def get_database() -> aiosqlite.Connection:
    """Get database connection."""
    if _database is None:
        return await connect_to_database()
    return _database


async def close_database() -> None:
    """Close database connection."""
    global _database
    if _database:
        await _database.close()
        _database = None
        logger.info("Database connection closed")


async def create_tables() -> None:
    """Create database tables if they don't exist."""
    db = await get_database()
    
    try:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                password_hash TEXT NOT NULL,
                subscription TEXT DEFAULT 'FREE',
                api_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                email_verified BOOLEAN DEFAULT FALSE,
                newsletter_subscription BOOLEAN DEFAULT FALSE,
                company TEXT,
                job_title TEXT,
                phone TEXT,
                timezone TEXT DEFAULT 'UTC',
                language TEXT DEFAULT 'en',
                country TEXT DEFAULT 'US',
                preferences TEXT  -- JSON stored as text
            )
        """)
        
        # Conversions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                input_format TEXT NOT NULL,
                output_format TEXT NOT NULL,
                input_filename TEXT NOT NULL,
                output_filename TEXT,
                file_size INTEGER,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                processing_time REAL,
                download_url TEXT,
                error_message TEXT,
                options TEXT,  -- JSON stored as text
                metadata TEXT,  -- JSON stored as text
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # API Keys table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                permissions TEXT,  -- JSON stored as text
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                usage_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Password resets table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Batch jobs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS batch_jobs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                options TEXT,  -- JSON stored as text
                files TEXT,  -- JSON stored as text
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Conversion templates table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversion_templates (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                input_format TEXT NOT NULL,
                output_format TEXT NOT NULL,
                options TEXT,  -- JSON stored as text
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create indexes for better performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversions_user_id ON conversions (user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversions_status ON conversions (status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversions_created_at ON conversions (created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys (user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_password_resets_email ON password_resets (email)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_password_resets_token ON password_resets (token)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON batch_jobs (user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_templates_user_id ON conversion_templates (user_id)")
        
        await db.commit()
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        await db.rollback()
        raise


async def health_check() -> dict:
    """Check database health."""
    try:
        db = await get_database()
        
        # Test basic connectivity
        start_time = asyncio.get_event_loop().time()
        await db.execute("SELECT 1")
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Get database file size
        file_size = _database_path.stat().st_size if _database_path and _database_path.exists() else 0
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "database_path": str(_database_path),
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Database utility functions
async def execute_query(query: str, params: tuple = ()) -> aiosqlite.Cursor:
    """Execute a query and return cursor."""
    db = await get_database()
    return await db.execute(query, params)


async def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute query and fetch one row as dictionary."""
    db = await get_database()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(query, params)
    row = await cursor.fetchone()
    return dict(row) if row else None


async def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute query and fetch all rows as list of dictionaries."""
    db = await get_database()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def insert_record(table: str, data: Dict[str, Any]) -> str:
    """Insert a record and return the ID."""
    db = await get_database()
    
    # Convert any dict/list values to JSON strings
    processed_data = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            processed_data[key] = json.dumps(value)
        else:
            processed_data[key] = value
    
    columns = ", ".join(processed_data.keys())
    placeholders = ", ".join(["?" for _ in processed_data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    await db.execute(query, list(processed_data.values()))
    await db.commit()
    
    # Return the inserted ID (assuming 'id' column exists)
    if 'id' in data:
        return data['id']
    else:
        # For auto-generated IDs
        cursor = await db.execute("SELECT last_insert_rowid()")
        result = await cursor.fetchone()
        return str(result[0]) if result else None


async def update_record(table: str, record_id: str, data: Dict[str, Any]) -> bool:
    """Update a record by ID."""
    db = await get_database()
    
    # Convert any dict/list values to JSON strings
    processed_data = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            processed_data[key] = json.dumps(value)
        else:
            processed_data[key] = value
    
    set_clause = ", ".join([f"{key} = ?" for key in processed_data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    
    cursor = await db.execute(query, list(processed_data.values()) + [record_id])
    await db.commit()
    
    return cursor.rowcount > 0


async def delete_record(table: str, record_id: str) -> bool:
    """Delete a record by ID."""
    db = await get_database()
    cursor = await db.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
    await db.commit()
    return cursor.rowcount > 0