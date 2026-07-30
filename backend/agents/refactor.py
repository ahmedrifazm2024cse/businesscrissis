import os

agents_dir = os.path.dirname(os.path.abspath(__file__))

def refactor_main_to_router(agent_path):
    main_py = os.path.join(agent_path, "main.py")
    if not os.path.exists(main_py):
        print(f"Skipping {agent_path}, no main.py")
        return

    with open(main_py, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    
    # Imports to add
    new_lines.append("from fastapi import APIRouter")
    new_lines.append("")
    
    in_lifespan = False
    
    for line in lines:
        # Replace FastAPI import if exists
        if "from fastapi import FastAPI" in line:
            continue # We already added APIRouter
            
        if "app = FastAPI" in line:
            new_lines.append("router = APIRouter()")
            continue
            
        if line.startswith("@app."):
            new_lines.append(line.replace("@app.", "@router."))
            continue
            
        if "if __name__ == " in line:
            break # Stop at uvicorn.run block
            
        # Optional: remove lifespan context since it will be handled globally
        if "async def lifespan" in line:
            in_lifespan = True
            
        if in_lifespan:
            if line.strip() == "yield":
                pass
            # We don't necessarily want to delete lifespan entirely if it contains important setup,
            # but in Phase 1 we moved DB init to global lifespan. We'll leave it as commented code.
            new_lines.append("# " + line)
            if "yield" in line:
                in_lifespan = False
            continue
            
        new_lines.append(line)

    router_py = os.path.join(agent_path, "router.py")
    with open(router_py, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
        
    print(f"Refactored {agent_path}/main.py to router.py")

for agent in os.listdir(agents_dir):
    agent_path = os.path.join(agents_dir, agent)
    if os.path.isdir(agent_path):
        refactor_main_to_router(agent_path)
