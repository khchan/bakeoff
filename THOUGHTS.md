# Thoughts

## Initial Goals
- Started with goal of using the newer Agent paradigms in Semantic Kernel with heavier reliance on tool calling
- Vena's model APIs seemed like a natural fit for at least putting together a POC of our current offering
- Wanted to see how far we can get leaning into tool calling and agent interop
- Leverage chainlit for quick interface and working through the ergonomics of each framework

## Track 1 (Semantic Kernel):
- Core concepts were easy to pick up, but documentation on the internet is lacking (github repo is how the team maintains examples)
- Process runtime workflows seems inspired from Autogen and appears to be the new primitive driving multi-agent collaboration
- Threading abstraction worked well as a concept that was passed around easily
- `AgentGroupChat` is transitioning to new [orchestration primitives](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/?pivots=programming-language-python)
- Sequential orchestration works reliably; group chat and handoff patterns encounter jailbreak violations haha, possibly due to SK's self-prompting mechanisms

## Track 2 (Claude Code vs Cursor Agent):
- Now with a working version for reference, I wanted to see how well I could vibe code other implementations in comparable frameworks
- Claude code is an agentic coding tool that lives entirely in the terminal
- Worked really well with a combination of the plan mode and git worktrees
## Track 2 (OpenAI Agents):

## Track 3 (LangGraph):

## Track 4 (Agno):

## Outcomes

Comparative analysis on each of the framework implementations in this project (semantic-kernel, openai-agents, agno, and langgraph).  
Gather info about these requirements and how well each framework supports it: 
- conversation history/chat threads that account for tool call history
- (bonus) thread truncation management
- multi-agent orchestration patterns
- lifecycle hooks for the full agent lifecycle
- human-in-the-loop workflows to interrupt the agent flow and prompt the user for input before proceeding