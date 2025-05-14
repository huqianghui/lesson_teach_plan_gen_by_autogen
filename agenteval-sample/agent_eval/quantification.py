from __future__ import annotations

import json
from typing import List

from pydantic import BaseModel


class Quantification(BaseModel):
    """
    A class that represents quantification of the performance of a system using the provided criteria.
    """

    name: str
    results: str | int | float
    
    def __init__(self, name: str, results: str | int | float):
        """
        Args:
            name (str): The name of the quantification.
            results (str | int | float): The results of the quantification.
        """
        super().__init__(name=name, results=results)

    @staticmethod
    def parse_json_str(quantification: str) -> List[Quantification]:
        """
        Parse a json string into a list of Quantification objects.
        
        Args:
            quantification (str): A json string that represents a list of Quantification objects.
        Returns:
            List[Quantification]: A list of Quantification objects.
        """
        return [Quantification(k, v) for k, v in json.loads(quantification).items()]

    @staticmethod
    def write_json(quantification: List[Quantification]) -> str:
        """
        Write a list of Quantification objects into a json string.
        
        Args:
            quantification (List[Quantification]): A list of Quantification objects.
        Returns:
            str: A json string that represents a list of Quantification objects.
        """
        return json.dumps([q.model_dump() for q in quantification], indent=2)
