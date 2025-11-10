import os
import gradio as gr
from huggingface_hub import InferenceClient
import dotenv
from prometheus_client import start_http_server, Counter, Summary

pipe = None
stop_infrence = False

# --- Prometheus metrics ---
REQUEST_COUNTER       = Counter('app_requests_total',               'Total number of requests')
SUCCESSFUL_REQUESTS   = Counter('app_successful_requests_total',    'Total number of successful requests')
FAILED_REQUESTS       = Counter('app_failed_requests_total',        'Total number of failed requests')
REQUEST_DURATION      = Summary('app_request_duration_seconds',     'Time spent processing request')
LOCAL_MODEL_REQUESTS  = Counter('app_local_model_requests_total',   'Total number of requests using local model')
API_MODEL_REQUESTS    = Counter('app_api_model_requests_total',     'Total number of requests using API model')

dotenv.load_dotenv()

def summarize_text(
        text,
        hf_token: str,
        use_local_model: bool,
    ):
    """
    Summarize the text
    """
    global pipe
    
    # Track total requests
    REQUEST_COUNTER.inc()

    if text is None:
        return "No text inserted"

    if use_local_model:
        try:
            print("[MODE] local")
            # Track local model usage
            LOCAL_MODEL_REQUESTS.inc()
            
            # Measure request duration
            with REQUEST_DURATION.time():
                from transformers import pipeline
                if pipe is None:
                    pipe = pipeline("summarization" , model="Falconsai/medical_summarization")

                output = pipe(
                    text,
                    max_length = 1000,
                    min_length = 250,
                    do_sample = False,
                )
            
            SUCCESSFUL_REQUESTS.inc()
            return output[0]["summary_text"]

        except Exception as e:
            FAILED_REQUESTS.inc()
            return f"Error: {str(e)}"
    
    else:
        try:
            print("[MODE] api")
            # Track API model usage
            API_MODEL_REQUESTS.inc()
            
            # Use token from user input or fallback to .env
            token = hf_token.strip() if hf_token and hf_token.strip() else os.getenv("HF_TOKEN")
            
            if not token:
                FAILED_REQUESTS.inc()
                return "Error: HuggingFace token is required for API mode. Please provide a token or set HF_TOKEN in .env file."
            
            # Create client with the token
            client = InferenceClient(
                provider="hf-inference",
                api_key=token,
            )
            
            # Measure request duration
            with REQUEST_DURATION.time():
                # Use the summarization model
                output = client.summarization(text, model="Falconsai/medical_summarization")
            
            # Find the summary text
            if output:
                SUCCESSFUL_REQUESTS.inc()
                return output.summary_text
            else:
                FAILED_REQUESTS.inc()
                return "No summary result"
                
        except Exception as e:
            FAILED_REQUESTS.inc()
            return f"Error: {str(e)}"

# Create the Gradio interface
demo = gr.Interface(
    fn = summarize_text,
    inputs = [
        gr.Textbox(lines=15, label="Medical Text", placeholder="Enter medical text to summarize..."),
        gr.Textbox(label="HuggingFace Token", type="password", placeholder="Enter your HF token"),
        gr.Checkbox(label="Use Local Model", value=False)
    ],
    outputs = gr.Textbox(lines=15, label="Summary"),
    title = "Medical Text Summarization", 
    description = "Insert a medical text to summarize. For API mode, provide your HuggingFace token."
)

if __name__ == "__main__":
    # Start the Prometheus HTTP server
    start_http_server(8000)
    # Start the Gradio interface
    demo.launch()