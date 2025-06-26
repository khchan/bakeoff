# Dr. Toolcall, or how I learned to stop worrying and love the context window
---

## Initial Goal
- Started with wanting to understand the `Agent` abstractions in Semantic Kernel which rely much more on tool calling
- Vena's model APIs seemed like a natural fit for leveraging what's possible with tool calling

---
## Track 1 (Semantic Kernel):
- Core concepts were easy to pick up, but documentation on the internet is lacking (github repo is how the team maintains examples)
- Sequential orchestration works reliably; group chat and handoff patterns encounter jailbreak violations haha, possibly due to SK's self-prompting mechanisms
- Ended up leveraging plugins as agents and handling orchestration that way with relative success

---
## Track 2 (Claude Code):
- Now with a working version for reference, I wanted to see how well I could ✨vibe✨ code other implementations in comparable frameworks
- `Claude Code` is an CLI based agentic coding tool that lives entirely in the terminal
- Prompted claude to make a plan, reflect on the capabilities of a reference implementation and attempt to go out and replicate it in another framework
- **What worked:** 
  - Plan mode to iteratively collaborate on a plan before writing code
  - Leverage git worktrees to perform tasks in parallel with multiple claudes
  - Understanding codebases, referencing documentation
  - Creating diagrams
- **What didn't work:** 
  - Very token heavy
  - Definitely struggled with some frameworks more than others

---
## Track 3 (Vibe Checking Frameworks):
- `OpenAI Agents SDK` ergonomics felt similar to how the assistant API worked with similar concepts, and treats Agents as first class citizens and defining handoff criteria for delegation
- `LangGraph` leans very much into the state machine / graph concepts with having to specify state data and state transitions up front with Langchain sprinkled in to handle lower level abstractions
- `Agno` leaned towards Agents as first class citizens, but with more bells and whistles like adding state management and integrations with external storage services for chat history and vector databases

---
## Observations
- APIs != Tools 
- `Context engineering` is as important as `Prompt engineering`
___
## Next Steps
1. Continue experimenting with what's possible with tool calling
2. Comparative analysis on each of the framework implementations against our key requirements