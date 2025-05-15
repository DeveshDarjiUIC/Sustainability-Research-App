from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import time
import os
from werkzeug.utils import secure_filename
import uuid
import tempfile
import google.generativeai as genai
from google.generativeai.types import GenerationConfig # Import GenerationConfig

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow requests from your React frontend

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()  # Use system temp directory
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_pdf_with_gemini(api_key, file_path):
    """
    Analyzes a PDF file using Gemini API with controlled temperature for more deterministic results.
    
    Args:
        api_key: Google Gemini API key
        file_path: Path to the PDF file
        
    Returns:
        Analysis text from Gemini, or error message
    """
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Upload the file to Gemini
        pdf_file = genai.upload_file(path=file_path)
        
        # Wait for file processing to complete
        while pdf_file.state.name == "PROCESSING":
            time.sleep(2)  # Check every 2 seconds
            pdf_file = genai.get_file(name=pdf_file.name)
        
        if pdf_file.state.name != "ACTIVE":
            # It's good practice to try and delete the file from Gemini even if processing fails
            try:
                genai.delete_file(name=pdf_file.name)
                print(f"Cleaned up file {pdf_file.name} from Gemini after processing failure.")
            except Exception as cleanup_error:
                print(f"Warning: Failed to delete file {pdf_file.name} from Gemini server after processing failure: {cleanup_error}")
            return {"error": f"File processing failed. State: {pdf_file.state.name}"}
        
        # Select model and define prompt
        # Using gemini-1.5-flash as an example, as "gemini-2.5-pro-preview-03-25" might not be a standard or available model name.
        # Please ensure you are using a valid and available model name.
        # For example, "gemini-1.5-pro-latest" or "gemini-1.0-pro" are common.
        # Let's assume you intended a Pro model, for instance "gemini-1.5-pro-latest"
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest") # Ensure this model name is correct and available
        
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

 

🔹 6. Action Prioritization & Detailing 

Has a longlist of potential actions been developed from evidence base? 

Has a shortlist of high-priority actions been defined using specific criteria/tools (e.g., ASAP, AMIA, cost-benefit)? 

Does the plan assess the fit of actions within broader city agendas? 

Is there evidence of inclusive stakeholder engagement in prioritization? 

Has the city adopted a flexible, iterative planning process? 

 

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

 Consolidate the socres and give them as
 Section 1: Stakeholder & Community Engagement: Score
 Section 2: GHG Emissions Inventory: Score
 Section 3: Climate Change Risk Assessment (CCRA): Score
 Section 4: City Needs Assessment: Score
 Section 5: Strategy Identification: Score
 Section 6: Action Prioritization & Detailing: Score
 Section 7: Equity & Inclusivity: Score
 Section 8: Monitoring, Evaluation & Reporting (MER): Score

 
        """
        
        # Define generation configuration with a lower temperature
        # Temperature: Controls randomness. Lower values (e.g., 0.2) make output more deterministic.
        # Higher values (e.g., 0.8) make it more random. Default is often around 0.7-0.9.
        # For deterministic output, 0.0 is the lowest, but 0.1 or 0.2 can be good compromises.
        config = GenerationConfig(temperature=0.2) 
        
        # Generate content with the specified configuration
        response = model.generate_content(
            [prompt, pdf_file],
            generation_config=config  # Pass the config here
        )
        result = response.text
        
        # Clean up by deleting the file from Gemini
        try:
            genai.delete_file(name=pdf_file.name)
            print(f"Successfully deleted file {pdf_file.name} from Gemini server.")
        except Exception as cleanup_error:
            print(f"Warning: Failed to delete file {pdf_file.name} from Gemini server during final cleanup: {cleanup_error}")
        
        return {"result": result}
    
    except Exception as e:
        # If an error occurs before pdf_file is defined or if its name is not available,
        # we can't delete it.
        if 'pdf_file' in locals() and hasattr(pdf_file, 'name'):
            try:
                genai.delete_file(name=pdf_file.name)
                print(f"Cleaned up file {pdf_file.name} from Gemini after an exception.")
            except Exception as cleanup_error:
                print(f"Warning: Failed to delete file {pdf_file.name} from Gemini server after an exception: {cleanup_error}")
        return {"error": str(e)}
    

@app.route('/api/analyze-pdf', methods=['POST'])
def analyze_pdf():
    """API endpoint to analyze a PDF file using Gemini AI"""
    
    # Check if API key is provided
    api_key = request.form.get('api_key')
    if not api_key:
        return jsonify({"error": "Gemini API key is required"}), 400
    
    # Check if file is included in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check if file is allowed
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    try:
        # Generate a unique filename to avoid collisions
        unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(file_path)
        
        # Process the file with Gemini
        result = analyze_pdf_with_gemini(api_key, file_path)
        
        # Clean up the temporary file
        try:
            os.remove(file_path)
        except:
            pass  # Continue even if cleanup fails
        
        # Return the analysis result
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        
        return jsonify({"result": result["result"]}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    # Using port 8000 instead of 5000 to avoid conflicts with AirPlay on macOS
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)