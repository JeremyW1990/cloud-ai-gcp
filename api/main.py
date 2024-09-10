from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import yaml
from LLMs.openai.init_assistant import init_assistants
from api.LLMs.openai.api import initialize_openai_client

app = FastAPI()

class ContextRequest(BaseModel):
    user_id: str
    context: str
    OPENAI_API_KEY: str

@app.post("/context")
async def create_context(request: ContextRequest):
    try:

        # Extract variables
        user_id = request.user_id
        context = request.context
        api_key = request.OPENAI_API_KEY

        initialize_openai_client(api_key)

        # Read agents from YAML file
        yaml_path = os.path.join("api", "config", "agents.yaml")
        with open(yaml_path, 'r') as file:
            agents_data = yaml.safe_load(file)
        
        # Prepare agents data
        agents = [{"name": name, "instructions": instructions} for name, instructions in agents_data.items()]

        # Call init_assistants function with necessary parameters
        created_assistants = init_assistants(agents, api_key)

        return {"message": f"Context created for user_id: {user_id}", "assistants": created_assistants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)