from typing import Dict, List, Optional

from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage

from .criterion import Criterion
from .critic_agent import CriticAgent
from .quantifier_agent import QuantifierAgent
from .subcritic_agent import SubCriticAgent
from .verifier_agent import CriticSummarizerAgent
from .quantification import Quantification
from .task import Task


async def generate_criteria(
    model_client: ChatCompletionClient,
    task: Task = None,
    additional_instructions: str = "",
    max_round=2,
    use_subcritic: bool = False,
):
    """
    Creates a list of criteria for evaluating the utility of a given task.
    Args:
        model_client (ChatCompletionClient): The model client for ChatCompletion inference.
        task (Task): The task to evaluate.
        additional_instructions (str): Additional instructions for the criteria agent.
        max_round (int): The maximum number of rounds to run the conversation.
        use_subcritic (bool): Whether to use the subcritic agent to generate subcriteria.
    Returns:
        list: A list of Criterion objects for evaluating the utility of the given task.
    """
    critic = CriticAgent(
        system_message=CriticAgent.DEFAULT_SYSTEM_MESSAGE + "\n" + additional_instructions,
        model_client=model_client,
    )

    agents = [critic]

    if use_subcritic:
        subcritic = SubCriticAgent(
            model_client=model_client,
        )
        agents.append(subcritic)
    
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=max_round)
    termination = text_mention_termination | max_messages_termination
    
    team = RoundRobinGroupChat(agents, termination_condition=termination)

    group_chat_messages = team.run_stream(task=task.get_sys_message())
    
    criteria_messages = await Console(group_chat_messages)
    
    content = criteria_messages.messages[-1].content
    
    # need to strip out any extra code around the returned json
    content = content[content.find("[") : content.rfind("]") + 1]
    criteria = Criterion.parse_json_str(content)
    return criteria

async def generate_summarized_criteria_multiple_seeds(
    model_client: ChatCompletionClient,
    task: Task = None,
    additional_instructions: str = "",
    max_round=2,
    use_subcritic: bool = False,
    seed: Optional[int] = 10,
) -> List[Criterion]:
    """
    Creates a list of summarized criteria by running the generate_criteria multiple times (seed times) and then summarize the results.
    Args:
        model_client (ChatCompletionClient): The model client for ChatCompletion inference.
        task (Task): The task to evaluate.
        additional_instructions (str): Additional instructions for the criteria agent.
        max_round (int): The maximum number of rounds to run the conversation.
        use_subcritic (bool): Whether to use the subcritic agent to generate subcriteria.
        seed (int): The number of times to run the generate_criteria function.
    Returns:
        list: A list of Criterion objects for evaluating the utility of the given task.
    """
    all_criteria = ""
    for i in range(seed):
        criteria = await generate_criteria(
            model_client=model_client,
            task=task,
            additional_instructions=additional_instructions,
            max_round=max_round,
            use_subcritic=use_subcritic,
        )
        all_criteria += Criterion.write_json(criteria) + "\n"
    
    summarized_criteria_agent = CriticSummarizerAgent(
        model_client=model_client,
    )
    response = await summarized_criteria_agent.on_messages(
        [TextMessage(
            source="summarized_criteria_user",
            content=all_criteria,
        )],
        cancellation_token=CancellationToken(),
    )
    
    content = response.chat_message.content
    content = content[content.find("[") : content.rfind("]") + 1]
    summarized_criteria = Criterion.parse_json_str(content)

    return summarized_criteria


async def quantify_criteria(
    model_client: ChatCompletionClient,
    criteria: List[Criterion] = None,
    task: Task = None,
    test_case: str = "",
    ground_truth: str = "",
):
    """
    Quantifies the performance of a system using the provided criteria.
    Args:
        model_client (ChatCompletionClient): The model client for ChatCompletion inference.
        criteria ([Criterion]): A list of criteria for evaluating the utility of a given task.
        task (Task): The task to evaluate.
        test_case (str): The test case to evaluate.
        ground_truth (str): The ground truth for the test case.
    Returns:
        dict: A dictionary where the keys are the criteria and the values are the assessed performance based on accepted values for each criteria.
    """
    quantifier = QuantifierAgent(
        model_client=model_client,
    )
    
    response = await quantifier.on_messages(
        [TextMessage(
            source="quantifier_user",
            content=task.get_sys_message()
            + "Evaluation dictionary: "
            + Criterion.write_json(criteria)
            + "actual test case to evaluate: "
            + test_case,
        )],
        cancellation_token=CancellationToken(),
    )
    
    quantified_results = response.chat_message.content
    return {"actual_success": ground_truth, "estimated_performance": quantified_results}


async def quantify_criteria_multiple_seeds(
    model_client: ChatCompletionClient,
    criteria: List[Criterion] = None,
    task: Task = None,
    test_case: str = "",
    ground_truth: str = "",
    seeds: int = 10,
) -> Dict[int, List[Quantification]]:
    """
    Quantifies the performance of a system using the provided criteria multiple times (seeds) and returns all the results.
    Args:
        model_client (ChatCompletionClient): The model client for ChatCompletion inference.
        criteria ([Criterion]): A list of criteria for evaluating the utility of a given task.
        task (Task): The task to evaluate.
        test_case (str): The test case to evaluate.
        ground_truth (str): The ground truth for the test case.
        seeds (int): The number of times to run the quantify_criteria function.
    Returns:
        dict: A dictionary where the keys are the seeds and the values are the quantified results.
    """
    results = {}
    for i in range(seeds):
        response = await quantify_criteria(
            model_client=model_client,
            criteria=criteria,
            task=task,
            test_case=test_case,
            ground_truth=ground_truth,
        )
        results[i] = Quantification.parse_json_str(response["estimated_performance"])
    return results
