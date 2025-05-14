# AgentEval (AutoGen) Sample Implementation

This is a sample implementation of the AgentEval framework using AutoGen 0.4 version. It is a simple implementation that demonstrates how to use the framework to evaluate by Agent for *Summarization* task.

This implementation is based on the [[Roadmap]: Integrating AgentEval](https://github.com/microsoft/autogen/issues/2162)

## Sample Implementation

- [AgentEval Experiment Notebook](./agenteval_experiment.ipynb)
- [AgentEval Sample Library](./agent_eval/)
    - [Model Criteria](./agent_eval/criteria.py)
    - [Model Quantification](./agent_eval/quantification.py)
    - [Agent CriticAgent](./agent_eval/critic_agent.py)
    - [Agent SubCriticAgent](./agent_eval/subcritic_agent.py)
    - [Agent QuantifierAgent](./agent_eval/quantifier_agent.py)
    - [Agent CriticSummarizerAgent](./agent_eval/verifier_agent.py)
    - [Class Verify (compute coefficient of variation)](./agent_eval/verifier_agent.py)
    - [Orchestrator agent_eval](./agent_eval/agent_eval.py)
