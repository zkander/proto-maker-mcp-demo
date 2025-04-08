from github import Github
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_github_connection():
    load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    org_name = os.getenv("GITHUB_ORG")
    
    logger.info("Testing GitHub connection...")
    logger.info(f"Token (first 10 chars): {token[:10]}...")
    logger.info(f"Organization: {org_name}")
    
    try:
        # Initialize GitHub client
        g = Github(token)
        
        # Test authentication
        user = g.get_user()
        logger.info(f"Successfully authenticated as: {user.login}")
        
        # Test organization access
        org = g.get_organization(org_name)
        logger.info(f"Successfully accessed organization: {org.login}")
        
        # List permissions
        logger.info("Checking organization permissions...")
        if user.login in [member.login for member in org.get_members()]:
            logger.info("User is a member of the organization")
        else:
            logger.warning("User is NOT a member of the organization")
            
        # Test repository creation permission
        try:
            test_repo_name = "test-permissions-delete-me"
            repo = org.create_repo(
                name=test_repo_name,
                description="Test repository - will be deleted",
                private=True,
                auto_init=True
            )
            logger.info("Successfully created test repository")
            
            # Clean up test repository
            repo.delete()
            logger.info("Successfully deleted test repository")
        except Exception as e:
            logger.error(f"Failed to create/delete repository: {str(e)}")
        
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_github_connection() 