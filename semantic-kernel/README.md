# Semantic Kernel 

This sample uses the latest available version of Semantic Kernel (1.33.0) to see what cross agent collaboration may look like.

## Observations
- `AgentGroupChat` is getting ported to [orchestration primitives](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/?pivots=programming-language-python) relying on SK's new process runtime.
- Tried each of sequential, group, handoff and only sequential "kinda" worked.  The other ones kept getting flagged for jailbreak violations surprisingly?  Maybe the self-prompting in SK is too close to jailbreaking.