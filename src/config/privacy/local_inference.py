"""
Maya Private - Local Inference
Handles on-device inference using WebLLM or lightweight models.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Try to import WebLLM or fallback to mock implementation
try:
    # This is a placeholder - WebLLM would be imported from a JS bridge or WASM runtime
    # For now, we'll use a lightweight alternative
    WEBLLM_AVAILABLE = False
except ImportError:
    WEBLLM_AVAILABLE = False

# Fallback to a simple local model (e.g., using transformers with a small model)
LOCAL_MODEL = None

def initialize_local_model():
    """
    Initialize local inference model.
    For production, this could load:
    - WebLLM (via JavaScript bridge)
    - ONNX Runtime with quantized model
    - TinyLLM or similar lightweight model
    """
    global LOCAL_MODEL
    
    try:
        # Option 1: Try to use transformers with a small model
        try:
            from transformers import pipeline
            LOCAL_MODEL = pipeline(
                "text-generation",
                model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                device=-1  # CPU only
            )
            logger.info("✓ Local inference initialized with TinyLlama")
            return True
        except ImportError:
            pass
        
        # Option 2: Mock implementation for development
        logger.warning("⚠ Local inference not available - using mock implementation")
        LOCAL_MODEL = "mock"
        return False
    
    except Exception as e:
        logger.error(f"Failed to initialize local model: {e}")
        LOCAL_MODEL = "mock"
        return False


def run_local(prompt: str) -> str:
    """
    Execute local inference on the given prompt.
    
    Args:
        prompt: User input text
        
    Returns:
        Model response text
    """
    global LOCAL_MODEL
    
    # Initialize model if not already done
    if LOCAL_MODEL is None:
        initialize_local_model()
    
    try:
        # If we have a real model
        if LOCAL_MODEL and LOCAL_MODEL != "mock":
            response = LOCAL_MODEL(
                prompt,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                truncation=True
            )
            return response[0]["generated_text"]
        
        # Mock implementation for development/testing
        else:
            return generate_mock_response(prompt)
    
    except Exception as e:
        logger.error(f"Local inference failed: {e}")
        # Return a helpful error message
        return f"Local inference error: {str(e)}. Consider enabling cloud fallback."


def generate_mock_response(prompt: str) -> str:
    """
    Generate a mock response for development/testing.
    This is used when actual local models are not available.
    """
    responses = {
        "hello": "Hello! I'm running locally on your device using Maya Private mode.",
        "how are you": "I'm functioning well in local inference mode, ensuring your privacy.",
        "default": f"[Local Mock Response] I received your query locally: '{prompt[:50]}...'. "
                   f"This is a mock response. To enable real local inference, install TinyLlama or configure WebLLM."
    }
    
    prompt_lower = prompt.lower().strip()
    
    for key, response in responses.items():
        if key in prompt_lower:
            return response
    
    return responses["default"]


# Initialize on import (optional - can be done lazily)
if os.getenv("MAYA_PRIVATE_PRELOAD", "false").lower() == "true":
    initialize_local_model()
