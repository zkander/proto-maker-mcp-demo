import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_ORG = os.getenv("GITHUB_ORG")
    SEARCH_QUERY = "ai-prototype OR ml-prototype OR ui-prototype in:name language:javascript language:typescript language:python stars:>5 created:>2023-01-01"
    PORT = int(os.getenv("PORT", "3000"))
    
    # Add OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    
    # Company details
    COMPANY_DETAILS = {
        "name": "TechVision AI",
        "logo": """
        ⚡️ TV ⚡️
        """,
        "brand_colors": {
            "primary": "#4A90E2",
            "secondary": "#50E3C2",
            "accent": "#F5A623",
            "background": "#FFFFFF",
            "text": "#2C3E50"
        },
        "design_system": {
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            "typography": {
                "font_family": "Inter, system-ui, sans-serif",
                "heading_sizes": {
                    "h1": "2.5rem",
                    "h2": "2rem",
                    "h3": "1.75rem",
                    "h4": "1.5rem"
                }
            }
        }
    }
    
    TRANSFORM_RULES = {
        "style_guide": {
            "prefix": "tv-",  # TechVision prefix
            "component_structure": "atomic",
            "design_patterns": [
                "Use atomic design principles",
                "Follow SOLID principles",
                "Implement container/presenter pattern",
                "Use dependency injection",
            ],
            "naming_conventions": {
                "components": "PascalCase",
                "functions": "camelCase",
                "constants": "UPPER_SNAKE_CASE",
                "css_classes": "kebab-case"
            },
            "component_patterns": {
                "atoms": "tv-atom-[name]",
                "molecules": "tv-molecule-[name]",
                "organisms": "tv-organism-[name]",
                "templates": "tv-template-[name]",
                "pages": "tv-page-[name]"
            }
        }
    }

config = Config() 