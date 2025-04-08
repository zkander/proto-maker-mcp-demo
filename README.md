#  AI UI Transformer 🎨

A service that automatically transforms UI prototypes to match your company's design system using AI. Built with Model-Context Protocol (MCP) pattern for reliable AI transformations.

## 🌟 Features

- Search for trending AI prototypes with a UI on GitHub
- Clone and transform UI components to match your design system
- Apply company branding and styling automatically
- Generate detailed commit messages using AI
- Maintain code functionality while updating design
- Track and document all transformations

## 🛠 Setup

### Prerequisites

- Python 3.10+
- GitHub account with API access
- OpenAI API key
- Git installed

### Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/your-org/techvision-transformer
cd techvision-transformer
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```env
GITHUB_TOKEN=your_github_token
GITHUB_ORG=your_organization
OPENAI_API_KEY=your_openai_key
PORT=3000
```

## 🚀 Usage

1. Start the server:

```bash
python run_server.py
```

2. Run the test script:

```bash
python test_api.py
```

3. Interactive Selection:
   - View available AI UI prototypes
   - Choose a prototype by number (1-5)
   - Refresh results with 'r'
   - Transform another prototype after completion
   - Quit anytime with 'q'

Example session:

```
🔍 Searching for AI UI prototypes...

Found AI prototypes:
1. =================================================
📁 ai-chat-interface
⭐ Stars: 45
🔄 Forks: 12
...

Options:
1-5: Choose a prototype to transform
r: Refresh search results
q: Quit

Enter your choice: 1

🚀 Creating new repository: test-prototype-x8j2k9
...

Options:
1: Transform another prototype
q: Quit
```

## 🧬 Model-Context Protocol (MCP)

This project implements the Model-Context Protocol pattern for reliable AI transformations. Here's how it works:

### 1. Model Layer

The Model layer handles the AI transformation logic:

```python
async def get_llm_transformation(self, content: str, file_path: str) -> str:
    """Model layer: Handles AI transformation"""
    prompt = self.create_transformation_prompt(content, file_path)
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a UI transformation expert..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return self.process_response(response)
```

### 2. Context Layer

The Context layer provides company-specific rules and patterns:

```python
# config/config.py
COMPANY_DETAILS = {
    "name": "TechVision AI",
    "logo": "⚡️ TV ⚡️",
    "brand_colors": {
        "primary": "#4A90E2",
        "secondary": "#50E3C2"
    },
    "design_system": {
        "typography": {
            "font_family": "Inter, system-ui, sans-serif"
        }
    }
}

TRANSFORM_RULES = {
    "style_guide": {
        "prefix": "tv-",
        "component_structure": "atomic",
        "naming_conventions": {
            "components": "PascalCase",
            "css_classes": "kebab-case"
        }
    }
}
```

### 3. Protocol Layer

The Protocol layer defines how the Model and Context interact:

```python
class TransformationService:
    async def transform_project(self, project_path: str):
        """Protocol layer: Orchestrates the transformation process"""
        try:
            # Find UI files
            ui_files = self.find_ui_files(project_path)

            # Transform each file using Model-Context Protocol
            for file_path in ui_files:
                # 1. Get original content
                content = self.read_file(file_path)

                # 2. Apply transformation using Model with Context
                transformed = await self.get_llm_transformation(content, file_path)

                # 3. Save transformed content
                self.save_file(file_path, transformed)

                # 4. Document changes
                changes = await self.get_llm_change_description(
                    content, transformed, file_path
                )
                self.changes_made.append(changes)

            # 5. Commit changes with AI-generated message
            await self.commit_changes(repo)
            return True

        except Exception as e:
            self.logger.error(f"Error in transform_project: {str(e)}")
            raise
```

## 📝 API Endpoints

### Search Prototypes

```bash
GET /search-prototypes
```

Returns AI UI prototypes matching search criteria.

### Create from Prototype

```bash
POST /create-from-prototype
{
    "source_repo_url": "https://github.com/user/repo",
    "new_repo_name": "new-prototype"
}
```

Creates a new repository with transformed UI components.

## 🔄 Transformation Process

1. **Search**: Find suitable AI UI prototypes
2. **Clone**: Create new repository and clone prototype
3. **Transform**: Apply company design system using MCP
4. **Commit**: Push changes with AI-generated commit message

## 🛡️ Error Handling

The service includes comprehensive error handling:

- GitHub API rate limiting
- Invalid repositories
- Transformation failures
- File system errors

## 📊 Logging

Detailed logging is available for:

- Transformation progress
- File changes
- API responses
- Error tracking
