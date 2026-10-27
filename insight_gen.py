import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise Exception(f"Gemini API configuration failed: {str(e)}")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Insight Generator API is running"}

@app.get("/test-insights")
async def get_test_insights():
    """Test endpoint that returns sample insights"""
    logger.info("Fetching test insights")
    return {
        "insights": [
            "Positive: Your click-through rates are 15% higher than industry average.",
            "Negative: Competitors are investing 40% more in video content.",
            "Positive: Your conversion rates peak on Tuesday and Wednesday.",
            "Negative: Mobile traffic shows higher engagement but lower conversion.",
            "Positive: Your targeting covers more demographics than competitors.",
            "Negative: Competitor analysis shows they're optimizing budget better."
        ]
    }

@app.post("/insight_gen")
async def generate_insights():
    try:
        # Hard-coded CSV paths
        competitors_path = "/Users/shriya/Documents/GitHub/logo_detect/hackbuild-Elite/backend/ad_analysis_results.csv"
        campaigns_path = "/Users/shriya/Documents/GitHub/logo_detect/hackbuild-Elite/public/my_camp.csv"

        # Check if CSV files exist
        if not os.path.exists(competitors_path):
            logger.error(f"Competitors CSV not found at {competitors_path}")
            raise HTTPException(status_code=400, detail=f"Competitors CSV not found at {competitors_path}")
        if not os.path.exists(campaigns_path):
            logger.error(f"Campaigns CSV not found at {campaigns_path}")
            raise HTTPException(status_code=400, detail=f"Campaigns CSV not found at {campaigns_path}")

        # Load CSVs
        logger.info(f"Loading CSV files: {competitors_path}, {campaigns_path}")
        try:
            comp_df = pd.read_csv(competitors_path)
            camp_df = pd.read_csv(campaigns_path)
        except Exception as e:
            logger.error(f"Error reading CSV files: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to read CSV files: {str(e)}")

        # Validate dataframes
        if comp_df.empty or camp_df.empty:
            logger.error("One or both CSV files are empty")
            raise HTTPException(status_code=400, detail="CSV files cannot be empty")

        
        # Generate summaries
        comp_summary = f"""
        Competitors Data Summary:
        - Total records: {len(comp_df)}
        - Columns: {list(comp_df.columns)}
        - Data types: {comp_df.dtypes.to_dict()}
        - Statistical summary: {comp_df.describe(include="all").to_string()}
        """
        
        camp_summary = f"""
        Campaign Data Summary:
        - Total records: {len(camp_df)}
        - Columns: {list(camp_df.columns)}
        - Data types: {camp_df.dtypes.to_dict()}
        - Statistical summary: {camp_df.describe(include="all").to_string()}
        """

        # Enhanced prompt
        prompt = f"""
        You are an expert marketing strategist and data analyst. Analyze the provided campaign data (my data) and competitor data to generate specific, actionable positive and negative marketing insights by comparing them.

        Positive insights: Areas where my campaigns perform better than competitors (strengths).
        Negative insights: Areas where my campaigns perform worse than competitors or opportunities for improvement (weaknesses).

        IMPORTANT: Return ONLY valid JSON in this exact format (no markdown, no code fences, no additional text):

        {{
          "insights": [
            "Positive: specific actionable insight 1",
            "Negative: specific actionable insight 2",
            "Positive: specific actionable insight 3",
            "Negative: specific actionable insight 4",
            "Positive: specific actionable insight 5",
            "Negative: specific actionable insight 6"
          ]
        }}

        Generate exactly 3 positive and 3 negative insights (alternating starting with positive) that are:
        1. Specific and actionable
        2. Based on data comparisons between my campaigns and competitors
        3. Include metrics or percentages when possible
        4. Focus on opportunities for improvement in negative insights
        5. Address different aspects: targeting, content, timing, budget, channels

        Prefix each insight with "Positive: " or "Negative: " as shown.

        MY CAMPAIGN DATA:
        {camp_summary}

        COMPETITORS DATA:
        {comp_summary}
        """

        # Call Gemini API
        logger.info("Calling Gemini API for insights")
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
                
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(gemini_error)}")

        # Parse response
        logger.info("Parsing Gemini response")
        try:
            insights_json = json.loads(response_text)
            
            # Validate response structure
            if not isinstance(insights_json, dict):
                raise ValueError("Response is not a JSON object")
            if "insights" not in insights_json:
                raise ValueError("Response missing 'insights' key")
            if not isinstance(insights_json["insights"], list):
                raise ValueError("'insights' must be a list")
            if len(insights_json["insights"]) != 6:
                raise ValueError(f"Expected 6 insights, got {len(insights_json['insights'])}")
                
            logger.info("Successfully generated insights")
            return insights_json
            
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON parsing error: {str(json_error)}, Raw response: {response_text}")
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(json_error)}")
        except ValueError as val_error:
            logger.error(f"Validation error: {str(val_error)}, Raw response: {response_text}")
            raise HTTPException(status_code=500, detail=f"Invalid response format: {str(val_error)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"General error in insight_gen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)