"""
Logger Utilities for Auto-Blogger
Provides per-section logging with IST timestamps and persistent file storage.
"""

import os
import logging
import re
from datetime import datetime
from pathlib import Path
import pytz

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

class ISTFormatter(logging.Formatter):
    """Custom formatter that uses IST timezone"""
    
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, IST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def setup_section_logger(job_id: str, section_index: int, section_title: str) -> logging.Logger:
    """
    Create a dedicated logger for a specific blog section.
    
    Args:
        job_id: Unique job identifier (e.g., "DevOps-2025-12-29")
        section_index: Section number (0-indexed)
        section_title: Human-readable section title
        
    Returns:
        Configured logger instance
    """
    # Create log directory (Persistent Volume: /app/backend/logs -> /home/ec2-user/portfolio-logs)
    log_dir = Path(f"logs/auto_blogger/{job_id}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename (remove special chars, limit length)
    safe_title = re.sub(r'[^\w\s-]', '', section_title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]
    
    log_file = log_dir / f"{section_index:02d}_{safe_title}.log"
    
    # Create logger with unique name
    logger_name = f"autoblogger.{job_id}.section_{section_index}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with IST formatter
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    formatter = ISTFormatter(
        '[%(asctime)s IST] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.propagate = False  # Don't propagate to root logger
    
    return logger

def setup_agent_logger(job_id: str, agent_name: str) -> logging.Logger:
    """
    Create a logger for a specific agent (orchestrator, critic, polisher, publisher).
    
    Args:
        job_id: Unique job identifier
        agent_name: Agent name (e.g., "orchestrator", "critic")
        
    Returns:
        Configured logger instance
    """
    log_dir = Path(f"logs/auto_blogger/{job_id}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{agent_name}.log"
    
    logger_name = f"autoblogger.{job_id}.{agent_name}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    logger.handlers.clear()
    
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    formatter = ISTFormatter(
        '[%(asctime)s IST] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.propagate = False
    
    return logger

def log_api_call(logger: logging.Logger, model: str, prompt_tokens: int, 
                 completion_tokens: int, latency: float, status: str = "success"):
    """
    Log API call details in a structured format.
    
    Args:
        logger: Logger instance
        model: Model identifier
        prompt_tokens: Input token count
        completion_tokens: Output token count
        latency: Response time in seconds
        status: "success" or "error"
    """
    logger.info(f"API Call - Model: {model}")
    logger.info(f"API Call - Prompt tokens: {prompt_tokens}")
    logger.info(f"API Call - Completion tokens: {completion_tokens}")
    logger.info(f"API Call - Latency: {latency:.2f}s")
    logger.info(f"API Call - Status: {status}")

def log_section_completion(logger: logging.Logger, section_index: int, 
                           word_count: int, char_count: int):
    """
    Log section generation completion with metrics.
    
    Args:
        logger: Logger instance
        section_index: Section number
        word_count: Total words generated
        char_count: Total characters generated
    """
    logger.info(f"✅ Section {section_index} completed successfully")
    logger.info(f"Metrics - Words: {word_count}, Characters: {char_count}")

def create_job_metadata(job_id: str, category: str, started_at: datetime):
    """
    Create job metadata file with initial information.
    
    Args:
        job_id: Unique job identifier
        category: Blog category
        started_at: Job start timestamp (IST)
    """
    import json
    
    log_dir = Path(f"logs/auto_blogger/{job_id}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "job_id": job_id,
        "category": category,
        "started_at": started_at.strftime('%Y-%m-%d %H:%M:%S IST'),
        "status": "started"
    }
    
    metadata_file = log_dir / "job_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def update_job_metadata(job_id: str, updates: dict):
    """
    Update job metadata file with new information.
    
    Args:
        job_id: Unique job identifier
        updates: Dictionary of fields to update
    """
    import json
    
    metadata_file = Path(f"logs/auto_blogger/{job_id}/job_metadata.json")
    
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {"job_id": job_id}
    
    metadata.update(updates)
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
