import os
import logging
from pathlib import Path
from typing import List, Dict
import openai
from git import Repo, Actor
from ..config.config import config
import shutil

class TransformationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        openai.api_key = config.OPENAI_API_KEY
        self.author = Actor("TechVision AI Bot", "bot@techvision.ai")
        self.changes_made = []  # Track changes for commit message

    async def transform_project(self, project_path: str):
        try:
            repo = Repo(project_path)
            self.changes_made = []  # Reset changes for new project
            
            # Find UI files
            ui_files = self.find_ui_files(project_path)
            print(f"\n📂 Found {len(ui_files)} UI files to transform")
            
            # Transform each file
            for file_path in ui_files:
                await self.transform_file(file_path)
            
            # Generate and commit changes
            await self.commit_changes(repo)
            return True
            
        except Exception as e:
            self.logger.error(f"Error in transform_project: {str(e)}")
            raise

    def find_ui_files(self, project_path: str) -> list[str]:
        """Find UI files in the project"""
        ui_files = []
        ui_patterns = ['.html', '.css', '.js', '.jsx', '.tsx', '.vue']
        
        for root, _, files in os.walk(project_path):
            for file in files:
                if any(file.endswith(ext) for ext in ui_patterns):
                    ui_files.append(os.path.join(root, file))
                    print(f"✓ Found: {file}")
        
        return ui_files

    async def transform_file(self, file_path: str):
        try:
            print(f"\n🔄 Transforming: {os.path.basename(file_path)}")
            
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Get LLM transformation
            transformed_code = await self.get_llm_transformation(
                original_content, 
                file_path
            )

            # Save transformed code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transformed_code)

            # Get LLM to describe changes
            changes = await self.get_llm_change_description(
                original_content,
                transformed_code,
                file_path
            )
            self.changes_made.append(changes)
            
            print(f"✅ Transformed: {os.path.basename(file_path)}")
            print(f"📝 Changes: {changes}")

        except Exception as e:
            self.logger.error(f"Error transforming {file_path}: {str(e)}")
            raise

    async def get_llm_transformation(self, content: str, file_path: str) -> str:
        """Get LLM to transform the code"""
        style_guide = config.TRANSFORM_RULES['style_guide']
        company = config.COMPANY_DETAILS
        file_ext = os.path.splitext(file_path)[1]
        file_name = os.path.basename(file_path)

        prompt = f"""
        Transform this code according to TechVision AI's design system. You must return ONLY valid, compilable code.

        IMPORTANT - DO NOT CHANGE:
        - DO NOT change the component/file name: {file_name}
        - DO NOT change the file extension from {file_ext}
        - DO NOT add or suggest new files
        - DO NOT add file extensions in the code
        - DO NOT modify import/export paths
        - DO NOT rename existing components or functions

        File: {file_name}
        Type: {file_ext}

        Company Details:
        - Name: {company['name']}
        - Logo: {company['logo']}
        
        Brand Colors:
        - Primary: {company['brand_colors']['primary']}
        - Secondary: {company['brand_colors']['secondary']}
        - Accent: {company['brand_colors']['accent']}
        - Background: {company['brand_colors']['background']}
        - Text: {company['brand_colors']['text']}

        Typography:
        - Font Family: {company['design_system']['typography']['font_family']}
        - Heading Sizes: {company['design_system']['typography']['heading_sizes']}
        
        Design Rules:
        - Component Prefix: {style_guide['prefix']}
        - Structure: {style_guide['component_structure']}
        - Naming Conventions:
          * Components: {style_guide['naming_conventions']['components']}
          * Functions: {style_guide['naming_conventions']['functions']}
          * CSS Classes: {style_guide['naming_conventions']['css_classes']}

        Original code:
        ```{file_ext}
        {content}
        ```
        
        CRITICAL REQUIREMENTS:
        1. Return ONLY the transformed code, no explanations or markdown
        2. Keep the EXACT same component/file name as {file_name}
        3. DO NOT add .tsx, .jsx, or any extensions in the code
        4. Keep all existing import/export statements as they are
        5. Maintain the same file structure and dependencies
        6. Only modify:
           - Styling (colors, typography, spacing)
           - CSS class names (add prefix)
           - Add company branding comments at top
           - Component internal structure
        7. Ensure proper syntax and compilation
        8. Keep indentation and formatting clean

        IMPORTANT: Your response must contain ONLY the transformed code that can be directly saved and compiled.
        DO NOT include any other text, markdown, or explanations.
        DO NOT suggest file renames or new files.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a UI transformation expert. Transform ONLY the code content, keeping all file names and structures exactly as they are."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Lower temperature for more consistent output
        )
        
        # Get only the code from the response
        transformed_code = response.choices[0].message.content.strip()
        
        # Remove any markdown code blocks if they exist
        if transformed_code.startswith("```"):
            transformed_code = transformed_code.split("```")[1]
            if transformed_code.startswith(file_ext):
                transformed_code = transformed_code[len(file_ext):].strip()
        
        # Additional cleanup to remove any file extension references
        transformed_code = transformed_code.replace('.tsx', '').replace('.jsx', '').replace('.js', '')
        
        return transformed_code

    async def get_llm_change_description(self, original: str, transformed: str, file_path: str) -> str:
        """Get LLM to describe the changes made"""
        prompt = f"""
        Describe the key changes made to this file:
        
        File: {os.path.basename(file_path)}
        
        Original vs Transformed code:
        ```diff
        {original}
        ---
        {transformed}
        ```
        
        Provide a brief, specific description of the changes made.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a code review expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    async def commit_changes(self, repo: Repo):
        """Commit and push changes with LLM-generated message"""
        try:
            # Stage changes
            repo.git.add('.')
            
            # Get LLM to generate commit message
            commit_message = await self.get_llm_commit_message()
            
            # Commit and push
            repo.index.commit(commit_message, author=self.author)
            repo.remote('origin').push()
            
            print("\n✨ Committed and pushed changes:")
            print(commit_message)
            
        except Exception as e:
            self.logger.error(f"Error in commit_changes: {str(e)}")
            raise

    async def get_llm_commit_message(self) -> str:
        """Get LLM to generate commit message from changes"""
        changes_text = "\n".join(self.changes_made)
        
        prompt = f"""
        Generate a clear commit message for these changes:
        
        Changes made:
        {changes_text}
        
        Format:
        - Start with an emoji and brief title
        - List key changes
        - Keep it concise but informative
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a commit message expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content 