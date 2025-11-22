"""
Maya Private - Remote Inference
Handles cloud-based inference using OpenAI as fallback for large contexts.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Install with: pip install openai")

# Configure OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def run_cloud(prompt: str) -> str:
    """
    Execute cloud inference using OpenAI as fallback.
    This is called when:
    - Context is too large for local inference
    - Local inference fails
    
    Args:
        prompt: User input text
        
    Returns:
        Model response text
    """
    if not OPENAI_AVAILABLE:
        return "Cloud inference unavailable: OpenAI package not installed. Install with: pip install openai"
    
    if not OPENAI_API_KEY:
        return "Cloud inference unavailable: OPENAI_API_KEY not configured in environment variables."
    
    try:
        # Use newer OpenAI client (v1.0+)
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are Maya in Private mode. This query was offloaded to the cloud due to size constraints. Respond naturally and concisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
    
    except ImportError:
        # Fallback to older OpenAI API (pre-v1.0)
        try:
            openai.api_key = OPENAI_API_KEY
            
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Maya in Private mode. This query was offloaded to the cloud due to size constraints."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            return resp.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Cloud inference failed (legacy API): {e}")
            return f"Cloud inference error: {str(e)}"
    
    except Exception as e:
        logger.error(f"Cloud inference failed: {e}")
        return f"Cloud inference error: {str(e)}"
