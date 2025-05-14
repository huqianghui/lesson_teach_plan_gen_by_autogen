from __future__ import annotations

import json
from typing import List

from pydantic import BaseModel


class Criterion(BaseModel):
    """
    A class that represents a criterion for agent evaluation.
    """

    name: str
    description: str
    accepted_values: List[str | int | float]
    sub_criteria: List[Criterion] = list()

    @staticmethod
    def parse_json_str(criteria: str):
        """
        Create a list of Criterion objects from a json string.
        Args:
            criteria (str): Json string that represents the criteria
        returns:
            [Criterion]: A list of Criterion objects that represents the json criteria information.
        """
        return [Criterion(**crit) for crit in json.loads(criteria)]

    @staticmethod
    def write_json(criteria):
        """
        Create a json string from a list of Criterion objects.
        Args:
            criteria ([Criterion]): A list of Criterion objects.
        Returns:
            str: A json string that represents the list of Criterion objects.
        """
        return json.dumps([crit.model_dump() for crit in criteria], indent=2)

    def convert_categorical_to_numerical(self, to_be_converted_value: str | int | float) -> int | float:
        """
        Convert the categorical values in the criterion to numerical values.
        
        Args:
            to_be_converted_value (str | int | float): The value to convert to numerical.
        Returns:
            int | float: The numerical value.
        """
        # Return if the accepted values are already numerical.
        if all(isinstance(value, (int, float)) for value in self.accepted_values) or isinstance(to_be_converted_value, (int, float)):
            return to_be_converted_value
        # Assign weights to the accepted values, where the first value has the highest weight 1 and the last value has the lowest weight 0.
        increment_magnitude = len(self.accepted_values) / (len(self.accepted_values) - 1) if len(self.accepted_values) > 1 else 1
        value_weights = {value: (len(self.accepted_values) - (i * increment_magnitude )) / len(self.accepted_values) for i, value in enumerate(self.accepted_values)}
        # Penalize the value if it is not in the accepted values.
        return value_weights[to_be_converted_value] if to_be_converted_value in value_weights else 0
        