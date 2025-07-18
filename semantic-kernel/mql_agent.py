from semantic_kernel.agents import ChatCompletionAgent
from chat_service import get_chat_service
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from utils import vena_client as vc

class MQLValidationPlugin:
    @kernel_function(
        description="Validate an MQL query against a model given the model ID and MQL expression to ensure it is correct",
        name="validate_mql"
    )
    def validate_mql(self, model_id: int, mql: str) -> str:
        return vc.validate_mql(model_id, mql)

def get_mql_agent():
    return ChatCompletionAgent(
        service=get_chat_service(),
        name="ModelQueryLanguageAgent",
        description="An expert FP&A assistant who writes syntactically-correct Vena MQL",
        plugins=[MQLValidationPlugin()],
        instructions="""### Task
    You are an expert FP&A assistant who writes syntactically-correct Vena MQL.
    
    ### Tips
    • MQL is *not* case-sensitive.  
    • Each dimension clause follows the pattern:
        dimension("<Dimension Name>": <Member Expression>)
    • Separate multiple dimension clauses and multiple items inside a clause with a single space.  
    • You can use the validate_mql(model_id: int, mql: str) function to validate the MQL expression.

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
    - This example demonstrates how to pull specific member datasets from one dimension using the union operator.

    Example 2: Combined Bottom Levels, two dimensions with exclusion
    dimension('Account': union(bottomlevel('Assets') bottomlevel('Liabilities')))
    dimension('Period': subtract(bottomlevel('Full Year') ichildren('Q1')))
    Return:
    - Within the Account dimension, all members at the bottom level of Assets plus all members at the bottom level of Liabilities.
    - All members of the Period dimension except children of Q1 as well as the member itself.
    - This example shows how different criteria may be used on different dimensions.

    Example 3: Bottom-level without a given attribute
    dimension('Account': subtract(  bottomlevel('Net Income') attribute(@' Static accounts '))) 
    Return:
    - Within the Account dimension, all members at the bottom level of Net Income, except for members with the attribute Static accounts.
    - This is an example of an expression used for a calculated member, where the dimension is omitted and only the member expression is written.

    Example 4: Intersection with an exclusion
    dimension('Account': intersection(descendants('Net Income') not(children('Cost of Revenue'))))
    Return:
    - Within the Account dimension, all members that are descendants of Net Income, except for children of Cost of Revenue.
    - This example illustrates how the intersection operator can be used as a filter to include all members under a given parent except the children of one of its children. The same could also be achieved with the union and not operators.
    
    ### Expected Output Format
    Return the MQL expression as a string with a space between each dimension clause.
    dimension('<dimension1>': <mql expression>) dimension('<dimension2>': <mql expression>) ...
    """
    )