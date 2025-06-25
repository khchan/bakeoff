import json
from typing import Dict, Any
from state import GraphState, Member, ModelInfo
from chat_service import get_chat_service
from tool_calls import make_tool_call

async def orchestration_node(state: GraphState) -> Dict[str, Any]:
    """Main orchestration node that decides the workflow path"""
    user_query = state["user_query"]
    
    # Determine if we need model selection
    messages = [
        {"role": "system", "content": """You are a helpful assistant that routes user queries to the appropriate agent.
        
        Analyze the user query and determine the next step:
        - "MODEL_SELECTION" if the user doesn't specify a model or you need to clarify which model
        - "MEMBER_PREDICTION" if the user has specified a model or is asking about a foundation/default model
        """},
        {"role": "user", "content": user_query}
    ]
    
    try:
        response = await get_chat_service().get_completion(messages, temperature=0.1)
        next_step = response.strip()
        
        return {
            "next_step": next_step,
            "tool_calls": state.get("tool_calls", [])
        }
    except Exception as e:
        return {
            "error": f"Orchestration error: {str(e)}",
            "tool_calls": state.get("tool_calls", []),
            "next_step": "ERROR"
        }

async def model_selection_node(state: GraphState) -> Dict[str, Any]:
    """Node for selecting the appropriate model"""
    try:
        # Get available models using tool call
        tool_call = await make_tool_call("list_models", {})
        models = tool_call["result"]  # Already a Python list, no JSON parsing needed
        
        # Track tool calls for UI
        tool_calls = state.get("tool_calls", [])
        tool_calls.append(tool_call)
        
        messages = [
            {"role": "system", "content": f"""You are a helpful assistant that helps users select the appropriate financial model.

Available models:
{json.dumps(models, indent=2)}

Determine which model the user is asking about. If it is unclear which model the user is talking about, clarify with the user. Once a SINGLE model is selected, respond with exactly: "SELECTED_MODEL_ID: <id>"

If you need clarification, ask the user which model they want to use.
"""},
            {"role": "user", "content": state["user_query"]}
        ]
        
        response = await get_chat_service().get_completion(messages, temperature=0.1)
        
        if "SELECTED_MODEL_ID:" in response:
            model_id = int(response.split("SELECTED_MODEL_ID:")[1].strip())
            selected_model = next((m for m in models if m["id"] == model_id), None)
            
            return {
                "selected_model": ModelInfo(
                    id=selected_model["id"],
                    name=selected_model["name"], 
                    description=selected_model["description"]
                ),
                "tool_calls": tool_calls,
                "next_step": "MEMBER_PREDICTION"
            }
        else:
            return {
                "response": response,
                "tool_calls": tool_calls,
                "next_step": "END"
            }
            
    except Exception as e:
        # Add more specific error information for debugging
        error_msg = f"Model selection error: {str(e)}"
        if "JSON" in str(e):
            error_msg += " (Data type issue - check tool call result format)"
        return {
            "error": error_msg,
            "tool_calls": state.get("tool_calls", []),
            "next_step": "ERROR"
        }

async def member_prediction_node(state: GraphState) -> Dict[str, Any]:
    """Node for predicting relevant OLAP members"""
    try:
        # Track tool calls for UI
        tool_calls = state.get("tool_calls", [])
        
        # Get model info if we have a selected model
        if state.get("selected_model"):
            model_id = state["selected_model"].id
            tool_call = await make_tool_call("get_model_info", {"id": model_id})
            model_info = tool_call["result"]
            tool_calls.append(tool_call)
        else:
            # Use default/foundation model logic
            list_tool_call = await make_tool_call("list_models", {})
            models = list_tool_call["result"]  # Already a Python list, no JSON parsing needed
            model_id = models[0]["id"]  # Use first model as default
            tool_calls.append(list_tool_call)
            
            model_tool_call = await make_tool_call("get_model_info", {"id": model_id})
            model_info = model_tool_call["result"]
            tool_calls.append(model_tool_call)
        
        messages = [
            {"role": "system", "content": f"""<task>
You are a helpful assistant that translates natural language questions into extracted members from a hierarchy in an OLAP cube.
</task>

<tips>
- The Account dimension type is almost always the most relevant dimension to answer questions about revenue.
</tips>

<instructions>
Phase 1: Model Selection
1. First, you should determine which model the user is asking about. Use the list_models() function to get a list of all available models.
2. You can then use the get_model_info(model_id: int) function to get dimension information about a specific model.
3. If it is unclear which model the user is talking about, clarify with the user. Once a SINGLE model is selected, you can move on to the next step.

Phase 2: Planning
4. Let's take is step by step. Reflect on the user's question and create a plan to predict which members from each dimension are relevant.

Phase 3: Member Search
5. If a member looks promising, you can use the search_members(model_id: int, dimension_id: int, query: str) function to search members until you have a list of all relevant members.
6. If you require more information, the query is unclear or there are no obvious candidates, call the get_top_level_members(model_id: int, dimension_number: int) function to start your search from the root of the dimension hierarchy (this will return the top-level members of the dimension).
7. If none of the top-level members look promising, you can call the get_children_of_member(model_id: int, dimension_number: int, member_id: str) function to continue drilling down to get the child members of each top-level member.
8. Once you have a list of members, reflect on the user's question and evaluate if you have enough information to answer the question.
</instructions>

<format>
You should return a list of members in the following format:
[
    {{
        "dimension": <dimension name>,
        "members": [
            {{
                "name": <member name>,
                "alias": <member alias>
            }},
            ...
        ]
    }}
]
</format>

Model Information:
{model_info}

User Query: {state["user_query"]}
"""},
            {"role": "user", "content": f"Find relevant members for this query: {state['user_query']}"}
        ]
        
        # For now, simulate member prediction - in a full implementation,
        # this would use the Vena API functions to search and find members
        response = await get_chat_service().get_completion(messages, temperature=0.1)
        
        # Parse predicted members (simplified for this example)
        predicted_members = [
            Member(name="Revenue", alias="Revenue", dimension="Account"),
            Member(name="2022", alias="2022", dimension="Period")
        ]
        
        return {
            "predicted_members": predicted_members,
            "tool_calls": tool_calls,
            "next_step": "MQL_GENERATION"
        }
        
    except Exception as e:
        return {
            "error": f"Member prediction error: {str(e)}",
            "tool_calls": state.get("tool_calls", []),
            "next_step": "ERROR"
        }

async def mql_generation_node(state: GraphState) -> Dict[str, Any]:
    """Node for generating Vena MQL queries"""
    try:
        members_info = []
        for member in state.get("predicted_members", []):
            members_info.append(f"Dimension: {member.dimension}, Member: {member.name} (alias: {member.alias})")
        
        members_str = "\n".join(members_info)
        
        messages = [
            {"role": "system", "content": """You are an expert FP&A assistant who writes syntactically-correct Vena MQL.
• MQL is *not* case-sensitive.  
• Each dimension clause follows the pattern:
    dimension("<Dimension Name>": <Member Expression>)
• Separate multiple dimension clauses and multiple items inside a clause with a single space.  
• If a dimension is omitted the query assumes *all* members of that dimension.  
• When defining a Calculated Member, omit the leading dimension("…": …) wrapper and provide only the member expression.

### Components you may use

1. Member — "'Member Name'"
2. Attribute — attribute(@'Attribute Name')
3. Function — one of:
- children(...)
- ichildren(...)
- descendants(...)
- idescendants(...)
- bottomlevel(...)
- ancestors(...)
- iancestors(...)
- parents(...)
4. Operator — one of:
- union(A B C …)
- intersection(A B …)
- subtract(A B)
- not(condition)

### Function behaviour
children            → direct children of the member  
ichildren           → member + its children  
descendants         → all descendants, parents listed before children  
idescendants        → member + all descendants, parents listed before children  
bottomlevel         → all bottom-level members under the member  
ancestors           → all ancestors of the member  
iancestors          → member + its ancestors  
parents             → direct parents of the member  

### Operator behaviour
union(A B …)        → combine the two (or more) sets  
intersection(A B)   → only elements common to every set  
subtract(A B)       → A minus the elements in B  
not(condition)      → everything *except* the condition  

### Examples
Example 1: Combined individual members
dimension('Account': union('5001' '5003'))
Return: 
- Within the Account dimension, the member 5001  plus the member 5003.
- The members of all other dimensions.
- This example demonstrates how to pull specific member datasets from one dimension using the union operator.

Example 2: Combined Bottom Levels, two dimensions with exclusion
dimension('Account': union(bottomlevel('Assets') bottomlevel('Liabilities')))
dimension('Period': subtract(bottomlevel('Full Year') ichildren('Q1')))
Return:
- Within the Account dimension, all members at the bottom level of Assets plus all members at the bottom level of Liabilities.
- All members of the Period dimension except children of Q1 as well as the member itself.
- The members of all other dimensions.
- This example shows how different criteria may be used on different dimensions.

Example 3: Bottom-level without a given attribute
dimension('Account': subtract(  bottomlevel('Net Income') attribute(@' Static accounts '))) 
Return:
- Within the Account dimension, all members at the bottom level of Net Income, except for members with the attribute Static accounts.
- The members of all other dimensions.
- This is an example of an expression used for a calculated member, where the dimension is omitted and only the member expression is written.

Example 4: Intersection with an exclusion
dimension('Account': intersection(descendants('Net Income') not(children('Cost of Revenue'))))
Return:
- Within the Account dimension, all members that are descendants of Net Income, except for children of Cost of Revenue.
- The members of all other dimensions.
- This example illustrates how the intersection operator can be used as a filter to include all members under a given parent except the children of one of its children. The same could also be achieved with the union and not operators.
"""},
            {"role": "user", "content": f"Generate MQL for:\nQuery: {state['user_query']}\nMembers: {members_str}"}
        ]
        
        mql = await get_chat_service().get_completion(messages, temperature=0.1)
        
        return {
            "generated_mql": mql,
            "tool_calls": state.get("tool_calls", []),
            "next_step": "RESPONSE_GENERATION"
        }
        
    except Exception as e:
        return {
            "error": f"MQL generation error: {str(e)}",
            "tool_calls": state.get("tool_calls", []),
            "next_step": "ERROR"
        }

async def response_generation_node(state: GraphState) -> Dict[str, Any]:
    """Node for generating the final response"""
    try:
        members_info = []
        for member in state.get("predicted_members", []):
            members_info.append(f"{member.dimension}: {member.name}")
        
        response = f"""Based on your query: "{state['user_query']}"

I've identified the following relevant members:
{', '.join(members_info)}

Generated MQL Query:
{state.get('generated_mql', 'No MQL generated')}

This query can be executed against your Vena model to retrieve the requested financial data."""
        
        return {
            "response": response,
            "tool_calls": state.get("tool_calls", []),
            "next_step": "END"
        }
        
    except Exception as e:
        return {
            "error": f"Response generation error: {str(e)}",
            "tool_calls": state.get("tool_calls", []),
            "next_step": "ERROR"
        }

async def error_node(state: GraphState) -> Dict[str, Any]:
    """Error handling node"""
    error_msg = state.get("error", "Unknown error occurred")
    return {
        "response": f"I encountered an error: {error_msg}. Please try rephrasing your question.",
        "tool_calls": state.get("tool_calls", []),
        "next_step": "END"
    }