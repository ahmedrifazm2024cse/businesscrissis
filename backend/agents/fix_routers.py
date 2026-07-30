import os
import re

agents_dir = os.path.dirname(os.path.abspath(__file__))

for root_dir, dirs, files in os.walk(agents_dir):
    if "router.py" in files:
        filepath = os.path.join(root_dir, "router.py")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Fix 1: trailing arguments after router = APIRouter()
        # Find router = APIRouter() and remove any trailing kwargs inside the same statement or next lines if they are hanging
        # Actually, it's easier to just match the pattern.
        # The previous script produced:
        # router = APIRouter()
        #     title=settings.PROJECT_NAME,
        #     openapi_url=...,
        #     lifespan=lifespan
        # )
        content = re.sub(r"router = APIRouter\(\)\s+title=.*?\)", "router = APIRouter()", content, flags=re.DOTALL)
        content = re.sub(r"router = APIRouter\(\)\s+title=.*?\n\)", "router = APIRouter()", content, flags=re.DOTALL)
        
        # A broader regex to catch hanging kwargs
        content = re.sub(r"router = APIRouter\(\)[\s]+title=.*?\)", "router = APIRouter()", content, flags=re.DOTALL | re.MULTILINE)
        
        # Or just find all hanging brackets
        lines = content.split("\n")
        new_lines = []
        skip_to_bracket = False
        for line in lines:
            if skip_to_bracket:
                if line.strip() == ")":
                    skip_to_bracket = False
                continue
                
            if line.startswith("router = APIRouter()"):
                new_lines.append(line)
                # Next line might be indented title=
                skip_to_bracket = True
                continue
                
            if skip_to_bracket and line.strip() == ")":
                skip_to_bracket = False
                continue
                
            if "app.add_middleware" in line:
                # skip middleware block
                skip_to_bracket = True
                if line.strip().endswith(")"):
                    skip_to_bracket = False
                continue
                
            if "app.include_router" in line:
                line = line.replace("app.include_router", "router.include_router")
                
            if "AgentverseWrapper(app)" in line:
                line = line.replace("AgentverseWrapper(app)", "AgentverseWrapper(router)")
                
            new_lines.append(line)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"Fixed {filepath}")
