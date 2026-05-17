# state_schema.py
from typing import TypedDict, List, Annotated
import operator

class ProcurementState(TypedDict):
    # --- Inputs ---
    query: str                # The raw user request
    
    # --- Agent Outputs ---
    extracted_data: dict      # Structured data from Planner (item, qty, price)
    total_base_cost: float   # Calculated before Audit
    audit_status: str         # "OK" or "VIOLATES" from Auditor
    audit_reason: str       # to store the policy explanation
    final_cost_with_duty: float  # Calculated after Audit
    inspector_notes: str      # Quality check notes from Inspector
    
    # --- Final Result ---
    final_output: str         # What the user eventually sees
    final_output_duty: str         # What the user eventually sees

    # --- Tracking ---
    # This 'operator.add' tells LangGraph: "Append new items to this list"
    internal_reasoning: Annotated[List[str], operator.add] # A log of what each agent did