import google.generativeai as genai
from pathlib import Path
import time
import os # Added for potentially getting API key from environment

# --- Function Definition ---
def getScores(api_key: str) -> str:
    """
    Prompts for a PDF file path, uploads it, analyzes it using Gemini
    with a fixed prompt, prints the response, and returns the response text.

    Args:
        api_key: Your Google Gemini API key.

    Returns:
        The analysis text from Gemini, or None if an error occurs.
    """
    # 1. Configure the Gemini API client
    try:
        genai.configure(api_key=api_key)
        print("Gemini API configured.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        print("Please ensure your API key is valid and has permissions.")
        return None # Indicate configuration failure

    # 2. Get PDF file path from terminal input
    pdf_path_str = input("Please enter the full path to the PDF file: ")
    pdf_path = Path(pdf_path_str.strip()) # Use pathlib and strip whitespace

    # 3. Validate the file path
    if not pdf_path.is_file():
        print(f"Error: File not found at '{pdf_path}'")
        return None
    if pdf_path.suffix.lower() != '.pdf':
        print(f"Error: The file '{pdf_path.name}' is not a PDF.")
        return None

    print(f"\nProcessing '{pdf_path.name}'...")
    pdf_file = None # Initialize pdf_file variable for cleanup in case of errors

    try:
        # 4. Upload the file using the Gemini File API
        print("Uploading file to Gemini...")
        # Consider adding display_name for clarity if needed
        pdf_file = genai.upload_file(path=pdf_path)
        print(f"Successfully uploaded '{pdf_path.name}' as file ID: {pdf_file.name}") # Using file ID is more precise

        # 5. Wait for the file processing to complete (IMPORTANT!)
        print("Waiting for file processing...")
        while pdf_file.state.name == "PROCESSING":
            time.sleep(5) # Check every 5 seconds (adjust as needed)
            # Fetch the file's updated state.
            pdf_file = genai.get_file(name=pdf_file.name)
            print(f"Current file state: {pdf_file.state.name}")

        if pdf_file.state.name != "ACTIVE":
            print(f"Error: File processing failed or file is not active.")
            print(f"Final state: {pdf_file.state.name}")
            # Attempt to delete the file if it exists in a non-ACTIVE state
            try:
                genai.delete_file(name=pdf_file.name)
                print(f"Cleaned up file {pdf_file.name} from server.")
            except Exception as delete_err:
                print(f"Note: Could not delete file {pdf_file.name} after processing failure: {delete_err}")
            return None

        print("File processed and ready for analysis.")

        # 6. Select the Gemini model
        # Use a model that supports file input, like 1.5 Flash or 1.5 Pro
        # Check the Gemini documentation for the latest models supporting File API
        model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25")

        # 7. Define the analysis prompt
        prompt = """
            Comprehensive Climate Action Plan Analysis 

You are tasked with analyzing a city’s Climate Action Plan (CAP) or related report. Based on the content, assess whether it addresses key areas across stakeholder engagement, emissions data, risk assessments, strategies, equity, and monitoring. 

Please respond using Yes/No and provide brief justifications or references where applicable. Where methods, tools, or stakeholder names are mentioned, list or summarize them clearly. Give me a comprehensive analysis along with scores. A “Yes” must be given a score of 1 and a “No” must be given a score of 0.  

Shape 

🔹 1. Stakeholder & Community Engagement 

1.1 Identifying Priority Stakeholders: 

Does the report identify groups most impacted by climate change (e.g., children, women, disabled, marginalized, frontline communities)? 

Are groups mentioned above excluded from previous engagement processes acknowledged? 

1.2 Engagement & Collaboration: 

Does the report mention planned engagement with private sector, national/regional governments, or other stakeholders? 

Has the city identified influential actors supportive of its climate plans? 

1.3 Engagement Methods: 

Have key stakeholders been integrated through long-term engagement throughout planning and implementation? If yes, which methods and groups? 

Has the broader public been engaged via surveys, consultations, summits, etc.? 

Shape 

🔹 2. GHG Emissions Inventory 

Is the city measuring GHG emissions? If yes, what methodology is used? 

Does it use a specific tool like for inventory management and reporting? 

Are the emissions inventory calculations publicly published? 

Shape 

🔹 3. Climate Change Risk Assessment (CCRA) 

Has the city conducted: 

A climate hazard assessment (probability, intensity, timescale)? 

A climate impact assessment (on people, infrastructure, services)? 

A full CCRA? A Climate Change Risk Assessment (CCRA) seeks to understand the likelihood of current and future climate hazards and the potential impacts of these hazards on cities and their inhabitants. 

Has the CCRA: 

Been outsourced? If so, to whom? 

Been updated or scheduled for renewal? 

Included interdependent risks and adaptive capacity analysis? 

Been made public? 

Shape 

🔹 4. City Needs Assessment 

Has the city analyzed socioeconomic context, environmental quality, and alignment with SDGs (Sustainable Development Goals) through strategic appraisal? 

Has it assessed city-wide priorities that climate actions could address? 

Shape 

🔹 5. Strategy Identification 

5.1 Mitigation Strategies: 

Has the city defined a planning horizon for its climate scenarios? 

Has a Business-As-Usual (BAU) forecast been included? 

Are modeling tools used for scenario development? 

Are mitigation projections based on current plans available? 

Is there an ambitious, long-term mitigation scenario? 

Adaptation Strategies: 

Has the city identified the root causes of climate risks? 

Reactive adaptation fights the immediate negative consequences of climate-related hazards, protecting quality of life and the city’s systems during climate-related disasters and restoring them afterwards. Are any reactive adaptation plans addressed 

Preventative adaptation reduces the negative consequences of climate-related hazards, aiming to protect quality of life and city systems to avoid those hazard events becoming disasters. Are any preventive adaptation plans included? 

Transformative adaptation tackles the root causes of climate risk, making climate-related hazards less likely or severe through fundamental changes to the city’s fabric and systems. Are any transformation adaptation plans included?  

Shape 

🔹 6. Action Prioritization & Detailing 

Has a longlist of potential actions been developed from evidence base? 

Has a shortlist of high-priority actions been defined using specific criteria/tools (e.g., ASAP, AMIA, cost-benefit)? 

Does the plan assess the fit of actions within broader city agendas? 

Is there evidence of inclusive stakeholder engagement in prioritization? 

Has the city adopted a flexible, iterative planning process? 

Shape 

🔹 7. Equity & Inclusivity 

7.1 Stakeholder Inclusion: 

Has the city included a diverse set of stakeholders in planning? (Yes/No) 

7.2 Needs & Vulnerability Assessment: 

Has the city identified vulnerable groups and reasons for vulnerability? (Yes/No) 

Has a comprehensive needs assessment been done? (Yes/No) 

7.3 Distributed Impact Analysis: 

Are equity impacts and challenges of actions analyzed? (Yes/No) 

Has the city used needs/stakeholder findings to guide climate actions? (Yes/No) 

7.4 Monitoring Equity: 

Is a Monitoring, Evaluation, and Reporting (MER) system used to track equity outcomes? 

Shape 

🔹 8. Monitoring, Evaluation & Reporting (MER) 

8.1 Integration with City Systems: 

Are existing climate plans and tracking mechanisms referenced? (Yes/No) 

Are inclusivity, public reporting, and data systems discussed? (Yes/No per question) 

8.2 Governance & Stakeholders: 

Are key stakeholders identified in MER? If yes, which ones? 

8.3 Defining Indicators: 

Are clear indicators set for each action (output, outcome, impact)? 

Are GHG, risk, and co-benefits included? 

8.4 Data Collection: 

Has the city identified data sources, ownership, collection methods, and reporting responsibilities? 

 

 

The scoring can be done in the way shown below. 

Counting the Yes/No Questions: 

Stakeholder & Community Engagement: 

1.1: Identify impacted groups? (1), Acknowledge excluded groups? (1) = 2 points 

1.2: Mention planned engagement? (1), Identified influential actors? (1) = 2 points 

1.3: Integrated key stakeholders? (1), Engaged broader public? (1) = 2 points 

Section 1 Total: 6 points 

GHG Emissions Inventory: 

Measuring GHG emissions? (1), Use a specific tool? (1), Calculations publicly published? (1) 

Section 2 Total: 3 points 

Climate Change Risk Assessment (CCRA): 

Conducted hazard assessment? (1), Conducted impact assessment? (1), Conducted full CCRA? (1), CCRA outsourced? (1), CCRA updated/scheduled? (1), Included interdependent risks/adaptive capacity? (1), CCRA made public? (1) 

Section 3 Total: 7 points 

City Needs Assessment: 

Analyzed socioeconomic context, etc.? (1), Assessed city-wide priorities? (1) 

Section 4 Total: 2 points 

Strategy Identification: 

5.1: Defined planning horizon? (1), Included BAU forecast? (1), Modeling tools used? (1), Mitigation projections available? (1), Ambitious long-term scenario? (1) = 5 points 

5.2: Identified root causes? (1), Reactive adaptation addressed? (1), Preventive adaptation included? (1), Transformative adaptation included? (1) = 4 points 

Section 5 Total: 9 points 

Action Prioritization & Detailing: 

Developed longlist? (1), Defined shortlist? (1), Assessed fit? (1), Evidence of inclusive engagement? (1), Adopted flexible process? (1) 

Section 6 Total: 5 points 

Equity & Inclusivity: 

7.1: Included diverse stakeholders? (1) = 1 point 

7.2: Identified vulnerable groups/reasons? (1), Comprehensive needs assessment? (1) = 2 points 

7.3: Equity impacts analyzed? (1), Used findings to guide actions? (1) = 2 points 

7.4: MER system used for equity? (1) = 1 point 

Section 7 Total: 6 points 

Monitoring, Evaluation & Reporting (MER): 

8.1: Existing plans referenced? (1), Inclusivity, public reporting, data systems discussed? (1)* = 2 points 

8.2: Key stakeholders identified in MER? (1) = 1 point 

8.3: Clear indicators set? (1), GHG, risk, co-benefits included? (1) = 2 points 

8.4: Identified data sources, etc.? (1) = 1 point 

Section 8 Total: 6 points 

Note on 8.1.2: The question "Are inclusivity, public reporting, and data systems discussed? (Yes/No per question)" is slightly ambiguous. It lists three items but asks a single question grammatically. Based on the singular structure "Are...discussed?", count it as a single point.  

Calculating the Total Maximum Score: 

Adding the maximum points from each section: 6 + 3 + 7 + 2 + 9 + 5 + 6 + 6 = 44 points 

Based on the provided structure and counting each distinct Yes/No question as one point, the maximum score any given report can get is 44. 

 

 
        """

        # 8. Generate the content
        print("Sending request to Gemini for analysis...")
        # Pass the file object directly in the list of contents
        response = model.generate_content([prompt, pdf_file])

        # --- Response Handling ---
        # 9. Print the response to the terminal
        print("\n--- Gemini Analysis Result ---")
        # Access the text part of the response
        # Add basic check if response or text is empty
        if response.text:
             print(response.text)
        else:
             print("[No text content received in the response]")
        print("--- End of Analysis ---")

        # 10. Return the response text
        return response.text

    except FileNotFoundError:
        # This case is technically handled by the initial check, but good practice
        print(f"Error: The file was not found at path: {pdf_path_str}")
        return None
    except Exception as e:
        # Catch potential API errors, network issues, or other exceptions
        print(f"\nAn error occurred during processing or analysis: {e}")
        # Consider more specific error handling based on google.api_core.exceptions if needed
        return None

    finally:
        # 11. Clean up: Delete the file from Gemini server regardless of success/failure after processing attempt
        if pdf_file and hasattr(pdf_file, 'name'):
            try:
                # Check state again before deleting, maybe not necessary but cautious
                # current_state = genai.get_file(name=pdf_file.name).state.name
                # print(f"File state before deletion attempt: {current_state}")
                genai.delete_file(name=pdf_file.name)
                print(f"\nDeleted file {pdf_file.name} from Gemini server.")
            except Exception as cleanup_error:
                print(f"\nWarning: Failed to delete file {pdf_file.name} from Gemini server: {cleanup_error}")
                print("You may need to delete it manually via the API or console.")


# --- Example Usage (How to call the function) ---
if __name__ == "__main__":
    # It's recommended to load API keys securely, e.g., from environment variables
    # For testing, you can replace "YOUR_API_KEY" directly, but avoid committing it.
    my_api_key = "AIzaSyC2YDjhWSh9VSGoKwlK1FRdvfcRKHMwiFk"# Try getting from environment variable first

    if not my_api_key:
         print("GEMINI_API_KEY environment variable not set.")
         # Fallback or direct assignment for testing (use cautiously):
         # my_api_key = "YOUR_ACTUAL_API_KEY"
         # if my_api_key == "YOUR_ACTUAL_API_KEY": # Remind user if placeholder is used
            # print("Please set the GEMINI_API_KEY environment variable or replace the placeholder in the code.")
         print("Attempting to run without API Key (will likely fail configuration).")
         # Or prompt the user for the key:
         my_api_key = input("Please enter your Gemini API Key: ")


    if my_api_key:
        print("\nStarting analysis process...")
        analysis_result = getScores(my_api_key)

        if analysis_result is not None:
            print("\nFunction execution completed. Analysis result obtained.")
            # The result is already printed within the function,
            # but you could do more with 'analysis_result' here if needed.
        else:
            print("\nFunction execution failed. See error messages above.")
    else:
        print("Cannot proceed without a Gemini API Key.")