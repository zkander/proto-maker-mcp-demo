from github import Github, GithubException
from git import Repo
from ..config.config import config
import logging
import os
import time
import shutil

class GitHubService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.github = Github(config.GITHUB_TOKEN, timeout=30, retry=3)
            # Test the connection
            user = self.github.get_user()
            self.logger.info(f"Authenticated as: {user.login}")
            
            # Test organization access
            try:
                self.org = self.github.get_organization(config.GITHUB_ORG)
                self.logger.info(f"Connected to organization: {self.org.login}")
            except GithubException as e:
                self.logger.error(f"Error accessing organization {config.GITHUB_ORG}: {str(e)}")
                raise
                
        except GithubException as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            if e.status == 401:
                self.logger.error("Token might be invalid or expired")
            raise
        except Exception as e:
            self.logger.error(f"Initialization error: {str(e)}")
            raise

    async def create_and_clone_repository(self, repo_name: str, target_path: str):
        try:
            # Create repository in GitHub
            repo = await self.create_repository(repo_name)
            
            # Clone the empty repository
            await self.clone_repository(repo.clone_url, target_path)
            
            return repo.clone_url
            
        except Exception as e:
            self.logger.error(f"Error creating/cloning repository: {str(e)}")
            raise

    async def create_repository(self, repo_name: str):
        try:
            # Check if repo exists
            try:
                repo = self.org.get_repo(repo_name)
                self.logger.info(f"Repository {repo_name} already exists")
                return repo
            except GithubException as e:
                if e.status == 404:
                    # Create new repository if it doesn't exist
                    try:
                        repo = self.org.create_repo(
                            name=repo_name,
                            description=f"Prototype repository: {repo_name}",
                            private=True,
                            auto_init=True
                        )
                        self.logger.info(f"Created new repository: {repo_name}")
                        return repo
                    except GithubException as create_error:
                        self.logger.error(f"Failed to create repository: {str(create_error)}")
                        raise
                else:
                    self.logger.error(f"Error checking repository: {str(e)}")
                    raise
                
        except Exception as e:
            self.logger.error(f"Error in create_repository: {str(e)}")
            raise

    async def search_prototypes(self):
        try:
            # Updated query to focus on modern AI UI prototypes
            queries = [
                "ai-chat-interface language:typescript stars:>20 created:>2023-01-01",
                "ai-dashboard template language:javascript stars:>20 created:>2023-01-01",
                "gpt-ui-template language:typescript stars:>10 created:>2023-01-01",
                "llm-interface fork:true language:javascript stars:>10 created:>2023-01-01",
                "chatbot-ui-template language:typescript stars:>10 created:>2023-01-01"
            ]
            
            results = []
            for query in queries:
                self.logger.info(f"Searching for AI UI prototypes with query: {query}")
                repositories = self.github.search_repositories(
                    query=query,
                    sort="stars",
                    order="desc"
                )
                
                for repo in repositories:
                    try:
                        # Check for UI-related files and AI components
                        contents = repo.get_contents("")
                        ui_files = []
                        ai_related = False
                        
                        for content in contents:
                            path = str(content.path).lower()
                            
                            # Check for UI files
                            if any(ext in path for ext in ['.html', '.css', '.jsx', '.tsx', '.vue']):
                                ui_files.append(path)
                            
                            # Check for AI-related patterns
                            ai_patterns = [
                                'chat', 'gpt', 'llm', 'ai', 'bot', 'completion',
                                'prompt', 'message', 'assistant', 'intelligence'
                            ]
                            if any(pattern in path for pattern in ai_patterns):
                                ai_related = True
                        
                        if ui_files and ai_related:
                            self.logger.info(f"Found AI UI prototype: {repo.name} with {len(ui_files)} UI files")
                            
                            # Get more detailed info about the repo
                            try:
                                readme = repo.get_readme().decoded_content.decode('utf-8').lower()
                                has_demo = 'demo' in readme or 'example' in readme
                            except:
                                has_demo = False
                            
                            results.append({
                                "name": repo.name,
                                "full_name": repo.full_name,
                                "description": repo.description,
                                "url": repo.clone_url,
                                "stars": repo.stargazers_count,
                                "updated_at": repo.updated_at.isoformat(),
                                "language": repo.language,
                                "topics": repo.get_topics(),
                                "ui_files": ui_files,
                                "has_demo": has_demo,
                                "forks_count": repo.forks_count
                            })
                            
                            if len(results) >= 5:  # Limit to top 5 results
                                break
                                
                    except Exception as e:
                        self.logger.warning(f"Error processing repository {repo.name}: {str(e)}")
                        continue
                        
                if len(results) >= 5:
                    break

            # Sort by stars and number of UI files
            results.sort(key=lambda x: (x['stars'], len(x['ui_files']), x['forks_count']), reverse=True)
            
            # Log found repositories
            self.logger.info("\nFound AI UI Prototypes:")
            for repo in results:
                self.logger.info(f"""
                    Name: {repo['name']}
                    Stars: {repo['stars']}
                    UI Files: {len(repo['ui_files'])}
                    Demo Available: {repo['has_demo']}
                    Description: {repo['description']}
                    URL: {repo['url']}
                    ---
                """)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching repositories: {str(e)}")
            raise

    async def clone_repository(self, repo_url: str, target_path: str):
        try:
            Repo.clone_from(repo_url, target_path)
            return True
        except Exception as e:
            self.logger.error(f"Error cloning repository: {str(e)}")
            raise

    async def clone_prototype_and_transform(self, source_repo_url: str, target_repo_name: str, target_path: str):
        try:
            print(f"\n🔍 Analyzing source repository: {source_repo_url}")
            
            # First create the new repository
            new_repo = await self.create_repository(target_repo_name)
            print(f"✓ Created new repository: {new_repo.name}")
            
            # Clone the source repository
            source_temp_dir = f"{target_path}_source"
            await self.clone_repository(source_repo_url, source_temp_dir)
            print(f"✓ Cloned source repository to: {source_temp_dir}")
            
            # Clone the new repository
            await self.clone_repository(new_repo.clone_url, target_path)
            print(f"✓ Cloned new repository to: {target_path}")
            
            # Copy files from source to target (excluding .git)
            print("\nCopying files to new repository:")
            copied_files = []
            for item in os.listdir(source_temp_dir):
                if item != '.git':
                    s = os.path.join(source_temp_dir, item)
                    d = os.path.join(target_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                        print(f"✓ Copied directory: {item}")
                    else:
                        shutil.copy2(s, d)
                        print(f"✓ Copied file: {item}")
                    copied_files.append(item)
            
            print(f"\n✓ Copied {len(copied_files)} items to new repository")
            
            # Clean up source temp directory
            shutil.rmtree(source_temp_dir)
            print("✓ Cleaned up temporary directory")
            
            return new_repo.clone_url
            
        except Exception as e:
            self.logger.error(f"Error in clone_prototype_and_transform: {str(e)}")
            print(f"❌ Failed to clone and transform: {str(e)}")
            raise 