from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import tempfile
import shutil
from pathlib import Path
import logging
from typing import Optional
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from .config.config import config
from .services.github_service import GitHubService
from .services.transformation_service import TransformationService

app = FastAPI(title="GitHub Prototype Transformer")

# Initialize services with error handling
try:
    logger.info("Initializing GitHub service...")
    github_service = GitHubService()
    logger.info("GitHub service initialized successfully")
    
    logger.info("Initializing Transformation service...")
    transformation_service = TransformationService()
    logger.info("Transformation service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

@app.on_event("startup")
async def startup_event():
    """Verify connections on startup"""
    try:
        # Test GitHub connection
        user = github_service.github.get_user()
        logger.info(f"Connected to GitHub as: {user.login}")
        
        # Test organization access
        org = github_service.org
        logger.info(f"Connected to organization: {org.login}")
    except Exception as e:
        logger.error(f"Startup check failed: {str(e)}")
        raise

class CreateFromPrototypeRequest(BaseModel):
    source_repo_url: str
    new_repo_name: str
    
    model_config = {
        "from_attributes": True
    }

@app.post("/create-from-prototype")
async def create_from_prototype(request: CreateFromPrototypeRequest):
    try:
        # Create temporary directory
        temp_dir = f"./temp/{request.new_repo_name}"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Clone prototype and create new repository
            repo_url = await github_service.clone_prototype_and_transform(
                request.source_repo_url,
                request.new_repo_name,
                temp_dir
            )
            
            # Transform the project
            await transformation_service.transform_project(temp_dir)
            
            return {
                "success": True,
                "message": "Project created from prototype, transformed, and pushed",
                "repo_url": repo_url,
                "branch": "main"
            }
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                
    except Exception as e:
        logger.error(f"Error in create_from_prototype: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-prototypes")
async def search_prototypes():
    try:
        prototypes = await github_service.search_prototypes()
        return {"success": True, "data": prototypes}
    except Exception as e:
        logger.error(f"Error in search_prototypes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        log_level="info"
    ) 