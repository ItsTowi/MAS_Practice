# src/mars_exploration/tools/markdown.py
from crewai.tools import BaseTool
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field

class MarkdownReaderInput(BaseModel):
    """Input for MarkdownReaderTool."""
    file_path: str = Field(
        ..., description="Path to the mission .md file."
    )

class MarkdownReaderTool(BaseTool):
    name: str = "Mission Report Reader"
    description: str = (
        "Reads the mission report in Markdown format. "
        "Useful for extracting scientific objectives, operational constraints, "
        "and known hazards."
    )
    args_schema: Type[BaseModel] = MarkdownReaderInput

    def _run(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: Mission report not found at {file_path}"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return f"Report content:\n\n{content}"
        except Exception as e:
            return f"Error reading the file: {str(e)}"
