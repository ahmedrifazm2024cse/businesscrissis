from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from core.config import settings
from typing import Any, Dict
import json
import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, agent_name: str, model_name: str = "gemini-2.5-pro"):
        self.agent_name = agent_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2, # Low temperature for more deterministic analysis
            convert_system_message_to_human=True
        )

    async def _invoke_llm(self, prompt_template: str, input_variables: Dict[str, Any], output_json: bool = True) -> Any:
        try:
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=list(input_variables.keys())
            )
            chain = prompt | self.llm
            response = await chain.ainvoke(input_variables)
            content = response.content
            
            if output_json:
                # Basic cleaning of markdown json blocks if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"[{self.agent_name}] Failed to parse JSON. Raw content: {content}")
                    # Return empty dict on parse error, but log it
                    return {}
            
            return content
        except Exception as e:
            logger.error(f"[{self.agent_name}] LLM Invocation failed: {e}")
            if output_json:
                return {}
            return ""
