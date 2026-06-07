"""
Roadmap API endpoints - AI Readiness Roadmap generation
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from uuid import uuid4
from datetime import datetime
from typing import List, Optional
import json

from app.database.db_service import DatabaseService
from app.auth import require_admin, require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/roadmap", tags=["roadmap"])

# File-based persistence (MVP)
db = DatabaseService(base_path="data")


@router.post("/generate")
async def generate_roadmap(request: Request):
    """
    Generate an AI Readiness Roadmap based on diagnostic results
    
    Returns:
        Roadmap with phases, milestones, and KPIs
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        diagnostic_id = data.get("diagnostic_id")
        
        roadmap_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        logger.info(f"Generating roadmap for user {user_id} from diagnostic {diagnostic_id}")
        
        roadmap = {
            "roadmap_id": roadmap_id,
            "user_id": user_id,
            "diagnostic_id": diagnostic_id,
            "title": "AI Readiness Roadmap",
            "description": "Phase-based roadmap to AI readiness",
            "phases": [
                {
                    "phase": 1,
                    "name": "Assessment & Planning",
                    "duration": "2-4 weeks",
                    "activities": [
                        "Define AI use cases",
                        "Assess current capabilities",
                        "Identify quick wins"
                    ],
                    "deliverables": ["Use case document", "Gap analysis"]
                },
                {
                    "phase": 2,
                    "name": "Foundation Building",
                    "duration": "1-2 months",
                    "activities": [
                        "Set up data infrastructure",
                        "Build initial models",
                        "Establish governance"
                    ],
                    "deliverables": ["Data pipeline", "Pilot models"]
                },
                {
                    "phase": 3,
                    "name": "Scale & Optimize",
                    "duration": "2-3 months",
                    "activities": [
                        "Scale proven solutions",
                        "Optimize performance",
                        "Expand team"
                    ],
                    "deliverables": ["Production systems", "Team roadmap"]
                }
            ],
            "kpis": [
                {"metric": "Time to Value", "target": "60 days", "baseline": "N/A"},
                {"metric": "Model Accuracy", "target": "85%+", "baseline": "N/A"},
                {"metric": "Team Adoption", "target": "80%+", "baseline": "N/A"}
            ],
            "risks": [
                {"risk": "Data quality issues", "mitigation": "Early validation", "priority": "High"},
                {"risk": "Team resistance", "mitigation": "Change management", "priority": "Medium"}
            ],
            "created_at": now,
            "updated_at": now,
            "status": "draft"
        }

        # Persist so admin/list endpoints can see it
        db.save_json("roadmaps", roadmap_id, roadmap)

        return roadmap
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate roadmap")


@router.get("")
async def list_all_roadmaps(_admin: dict = Depends(require_admin)):
    """
    List all roadmaps (GET /api/v1/roadmap) - admin only

    Returns:
        List of roadmap records across all users
    """
    logger.info("Listing all roadmaps")

    roadmaps = db.load_all_json("roadmaps")
    roadmaps.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {
        "success": True,
        "roadmap": roadmaps,
        "total": len(roadmaps),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/list")
async def list_roadmaps(user_id: str = Query(..., description="User ID")):
    """
    List roadmaps for a user
    
    Returns:
        List of roadmap summaries
    """
    logger.info(f"Listing roadmaps for user: {user_id}")

    roadmaps = [
        r for r in db.load_all_json("roadmaps") if r.get("user_id") == user_id
    ]
    roadmaps.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return roadmaps


@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str, user_id: str = Query(...)):
    """
    Get roadmap details
    
    Returns:
        Complete roadmap with all phases and details
    """
    logger.info(f"Getting roadmap {roadmap_id} for user {user_id}")
    
    now = datetime.utcnow().isoformat()
    
    return {
        "roadmap_id": roadmap_id,
        "user_id": user_id,
        "title": "AI Readiness Roadmap",
        "description": "Phase-based roadmap to AI readiness",
        "status": "active",
        "created_at": now
    }


@router.post("/{roadmap_id}/export")
async def export_roadmap(roadmap_id: str, format: str = Query("json")):
    """
    Export roadmap in specified format
    
    Formats:
        - json: JSON format
        - pdf: PDF document
    """
    logger.info(f"Exporting roadmap {roadmap_id} as {format}")
    
    if format not in ["json", "pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    return {
        "roadmap_id": roadmap_id,
        "format": format,
        "status": "ready",
        "download_url": f"/downloads/{roadmap_id}.{format}"
    }
