from langgraph.graph import StateGraph, END
from state_schema import ProcurementState
from planner import planner_node
from auditor import auditor_node
from inspector import inspector_node

# 1. Initialize Graph
workflow = StateGraph(ProcurementState)

# 2. Register Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("auditor", auditor_node)
workflow.add_node("inspector", inspector_node)

# 3. Define the routing function
def route_after_planner(state: ProcurementState):
    """
    Implements conditional routing logic to determine the next step in the 
    Agentic workflow based on the current state of the procurement cycle.

    This function acts as a decision-maker for the 'Hub' (Planner), routing the 
    process through a sequential loop:
    1. 'auditor': Triggered if the procurement request hasn't been checked 
       against policies yet.
    2. 'inspector': Triggered once the audit is complete but before final 
       QA validation.
    3. 'end': Triggered when both the audit and inspection have successfully 
       concluded, terminating the graph.

    Args:
        state (ProcurementState): The current global state of the conversation, 
                                  used to check for completed tasks.

    Returns:
        str: The name of the next node to execute ('auditor', 'inspector', or 'end').
    """
    # If Auditor hasn't run, go to auditor
    if not state.get("audit_status"):
        return "auditor"
    # If Inspector hasn't run, go to inspector
    elif not state.get("inspector_notes"):
        return "inspector"
    # Otherwise, we are done
    else:
        return "end"

# 4. Define the Flow
workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "auditor": "auditor",   # Matches node name in line 13
        "inspector": "inspector", # Matches node name in line 14
        "end": END
    }
)

# Return back to the hub (planner) after each task
workflow.add_edge("auditor", "planner")
workflow.add_edge("inspector", "planner")

# 5. Compile
app = workflow.compile()

# --- RUNNABLE BLOCK ---
if __name__ == "__main__":
    print("--- 🚀 STARTING PROCUREMENT GUARDIAN ---")
    
    user_query = input("Enter your procurement request: ")
    
    initial_input = {
        "query": user_query,
        "internal_reasoning": []
    }
    
    final_state = app.invoke(initial_input)
    
    print("\n" + "="*30)
    print("FINAL SYSTEM OUTPUT:")
    print(final_state.get("final_output", "No final output generated."))
    print("="*30)
    print("REASONING LOG:", final_state.get("internal_reasoning"))