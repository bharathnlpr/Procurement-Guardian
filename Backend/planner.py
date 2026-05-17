import os
import json
from google import genai
from dotenv import load_dotenv
# --- HERE IS THE CALL TO YOUR OTHER PROGRAM ---
from state_schema import ProcurementState 
from tools import calculate_import_duty
import time

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def planner_node(state: ProcurementState):
    """
    Orchestrates the procurement workflow by extracting data, calculating costs, 
    and coordinating with external tools based on the current audit status.

    This node operates in three primary phases:
    1. Initial Extraction: Parses the user query into structured JSON (item, qty, price, origin).
    2. Base Calculation: Ensures numerical consistency by synchronizing calculated totals 
       with the global state.
    3. Duty Calculation: If audit status is 'OK', it invokes the import duty tool and 
       generates a final coordinator report.

    Args:
        state (ProcurementState): The shared graph state containing the user query, 
                                  extracted data, and audit results.

    Returns:
        dict: Updated state keys including 'extracted_data', 'total_base_cost', 
              'final_cost_with_duty', and 'internal_reasoning'.
    """
    print("---Planner Node---")
    time.sleep(2) # Wait 2 seconds before calling the LLM

    # 1. THE "STOP" SIGN: If the job is already done, don't do anything.
    if state.get("final_output_duty"):
        print("Planner: System has already produced a final output. Ending cycle.")
        return state
    
    
    # 2. THE TOTAL COST (Before Audit)
    if state.get("extracted_data") and not state.get("total_base_cost"):
        print("Planner: 🧮 Calculating Base Total for the Auditor...")
        qty = state['extracted_data'].get('quantity', 0)
        price = state['extracted_data'].get('unit_price', 0)
        base_total = qty * price
        
        return {
            "extracted_data": {**state['extracted_data'], "total_base_cost": base_total},
            "total_base_cost": base_total, # <--- ADD THIS: Sync with main state
            "internal_reasoning": [f"Planner: Calculated base total of {base_total} KWD."]
        }
    
    
    # 3. THE DUTY CALCULATOR (After Audit "OK")
    if state.get("audit_status") == "OK" and not state.get("final_cost_with_duty"):
        print("Planner: ✅ Policy OK. Calling Tool for Import Duty...")
    
        # 1. Get the pre-verified value from the state
        base_val = state.get("total_base_cost", 0)

        # 2. CALL THE TOOL DIRECTLY for the state update
        # This ensures the state and the LLM are perfectly synchronized
        calculated_duty_total = calculate_import_duty(total_base_cost=base_val)

        # 3. INFORM THE MODEL about the tool and the result
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            config={
                "tools": [calculate_import_duty],
                "system_instruction": (
                    "You are the project coordinator. The policy audit is successful. "
                    f"The verified base cost is {base_val} KWD. "
                    f"The final cost after duty is {calculated_duty_total} KWD. "
                    "Provide a professional final summary report for the user."
                )
            },
            contents=f"Generate the final procurement report. Base: {base_val}, Final: {calculated_duty_total}."
        )

        return {
            "final_cost_with_duty": calculated_duty_total, # Value from the tool call
            "final_output_duty": response.text, 
            "internal_reasoning": [f"Planner: Calculated final duty total ({calculated_duty_total}) using the dedicated tool."]
        }

    # 4. THE "SKIP" LOGIC: If we have data but the Audit says "VIOLATES", 
    # we just pass through to the Inspector to handle the rejection.
    if state.get("extracted_data"):
            print("Planner: Data exists but policy is not 'OK'. Routing for inspection/correction...")
            return state # Just pass through to the conditional edge

    # 5. INPUT: Use state['query']
    user_input = state['query']
    
        # 6. YOUR TASK: Write your prompt here based on your Objectives
        # (Tell Gemini to extract the item, qty, price, and origin)
    my_prompt = f"""
    OBJECTIVE: You are the central main agent that coordinates all the jobs.

        Analyse the user input: "{user_input}"
        Extarct key data: (item_name, quantity, unit_price and origin)
        Return ONLY JSON.
    RULES:
        1. 'unit_price' MUST be a FLOAT (e.g., 350.0). Remove all currency symbols like 'KWD'.
        2. 'quantity' MUST be an INTEGER.
        3. Calculate 'total_base_cost' mathematically (quantity * unit_price).
    
    """

    # 7. LLM CALL:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=my_prompt,
        config={"response_mime_type": "application/json"} # Syntax for clean JSON
    )

    # 8. OUTPUT: Extract the raw JSON and the calculated total
    extracted_json = json.loads(response.text)
    base_val = extracted_json.get("total_base_cost", 0)

    return {
        "extracted_data": extracted_json,
        "total_base_cost": base_val, # <--- ADD THIS: Save to main state
        "internal_reasoning": ["Planner: Extracted request details and saved base cost."]
    }

