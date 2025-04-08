import uvicorn
import logging
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Verify environment variables
        token = os.getenv("GITHUB_TOKEN")
        org = os.getenv("GITHUB_ORG")
        
        if not token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")
        if not org:
            raise ValueError("GITHUB_ORG not found in environment variables")
            
        logger.info(f"Starting server with organization: {org}")
        logger.info(f"Token present (first 10 chars): {token[:10]}...")
        
        # Run the server
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "3000")),
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 