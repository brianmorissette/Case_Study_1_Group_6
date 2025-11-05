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

dotenv.load_dotenv()

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

def summarize_text(
        text,
        use_local_model: bool,
    ):
    """
    Summarize the text
    """
    global pipe

    if text is None:
        return "No text inserted"

    if use_local_model:
        try:
            print("[MODE] local")
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
    inputs = gr.Textbox(lines=15),
    additional_inputs = [
        gr.Checkbox(label="Use Local Model", value = False)
    ],
    outputs = gr.Textbox(lines=15),
    title = "Medical Text Summarization", 
    description = "Insert a medical text to summarize"
)

if __name__ == "__main__":
    # Start the Prometheus HTTP server
    start_http_server(8000)
    # Start the Gradio interface
    demo.launch()