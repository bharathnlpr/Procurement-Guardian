import os
from urllib import response
from google import genai
from dotenv import load_dotenv
from state_schema import ProcurementState
import time 

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def inspector_node(state: ProcurementState):
    """
    Acts as the final quality assurance gate in the agentic workflow.

    The Inspector performs a cross-validation between the 'Raw Data' (from the Planner) 
    and the 'Draft Report' (after Policy Auditing). It ensures that:
    1. Numerical data remains consistent across the entire transition.
    2. Policy violations identified by the Auditor are clearly communicated to the user.
    3. The final output maintains a professional, verified tone for approval or rejection.

    Args:
        state (ProcurementState): The global state containing extracted data, audit results, 
                                  and the draft duty report.

    Returns:
        dict: Finalized state updates including 'final_output', 'inspector_notes', 
              and persistent numerical metrics for the UI dashboard.
    """
    print("---Inspector Node---")
    time.sleep(2) # Wait 2 seconds before calling the LLM
    
    # 1. INPUT: Receives the full state to review the work of others
    # (Planner data and Auditor status)
    planner_data = state.get('extracted_data', {})
    audit_result = state.get('audit_status', '')
    duty_report = state.get("final_output_duty") # The report from the Planner
    audit_reason = state.get("audit_reason", "No reason provided.")
    
    # 2. SYSTEM INSTRUCTION: Write your Objective & Duties here
    inspector_instruction = """
    OBJECTIVE: You are the quality checker.

    DUTIES:
    1.Recieves the final outputs from planner_node.
    2.Revalidate all the datas befor the user sees it.
    3.It works a loop the recheck and corrects the output with planner_node.

    """

    # 3. PROMPT: Write your specific verification prompt here
    # (Tell Gemini to check for errors or inconsistencies)
    verification_prompt = f"""
        "You are the Final Quality Inspector. Review this procurement cycle: \n"
            f"1. RAW DATA: {planner_data} \n"
            f"2. AUDIT STATUS: {audit_result} \n"
            f"3. DRAFT REPORT: {duty_report} \n\n"
            f"4. VIOLATION DETAILS: {audit_reason} \n\n"
            "TASK: Revalidate everything. If the math and policy are sound, "
            "provide the FINAL approval report. Use a professional, verified tone "
            "similar to 'Verified' or 'Validated' status."
            "If VIOLATES, list the specific policy breaches clearly in your report."
        """
    # 4. LLM CALL
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={"system_instruction": inspector_instruction},
        contents=verification_prompt
    )

   # 5. OUTPUT: Update the inspector_notes, final_output, and carry over numbers
    return {
        "inspector_notes": response.text,
        "final_output": f"Final Report: {response.text}",
        "internal_reasoning": ["Inspector: Final quality check complete."],
        # --- ADD THESE LINES TO FIX THE UI ---
        "total_base_cost": state.get("total_base_cost"), 
        "final_cost_with_duty": state.get("final_cost_with_duty"),
        "audit_status": state.get("audit_status")
    }

