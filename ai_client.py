from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from config import azure_config
from typing import List
from abc import ABC, abstractmethod
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class AllergenInfo(BaseModel):
    """Structured response format for allergens"""
    allergens: List[str] = Field(
        description="List of identified allergenic ingredients",
    )

class AllergentExtractor(ABC):
    @abstractmethod
    def extract_allergens(self, ingridients: List[str]) -> AllergenInfo:
        pass


class AzureAIClient(AllergentExtractor):
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_config.endpoint,
            openai_api_version=azure_config.api_version,
            azure_deployment=azure_config.deployment,
            api_key=azure_config.api_key,
            temperature=config["model"]["temp"]
        ).with_structured_output(
            AllergenInfo,
            method="function_calling"
        )

    def extract_allergens(self, ingredients: List[str]) -> AllergenInfo:
        prompt = f"""Analyze these recipe ingredients and identify common allergens:
        
        Ingredients:
        {"\n".join(ingredients)}

        Return ONLY the identified allergens as a JSON array."""
        
        return self.llm.invoke(prompt)


if __name__ == "__main__":
    client = AzureAIClient()
    test_ingredients = [
        "2 cups all-purpose flour",
        "1 cup milk",
        "2 tablespoons soy sauce",
        "1/4 cup peanut butter"
    ]
    
    result = client.extract_allergens(test_ingredients)
    print("Identified allergens:", result.allergens)