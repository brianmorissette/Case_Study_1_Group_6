import os
import gradio as gr
from huggingface_hub import InferenceClient

pipe = None
stop_infrence = False

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

def summarize_text(text):
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
            import torch
            if pipe is None:
                pipe = pipeline("summarization" , model="Falconsai/medical_summarization")

            output = pipe(
                text,
                max_length = 2000,
                min_length = 1000,
                do_sample = False,
            )

            return output["summary_text"]

        except Exception as e:
            return f"Error: {str(e)}"
    
    else:
        try:
            # Use the summarization model
            output = client.summarization(text, model="Falconsai/medical_summarization")
            
            # Find the summary text
            if output:
                return output.summary_text
            else:
                return "No summary result"
                
        except Exception as e:
            return f"Error: {str(e)}"

# Create the Gradio interface
demo = gr.Interface(
    fn = summarize_text,
    inputs = gr.Textbox(type="text"),
    additional_inputs = [
        gr.Checkbox(label="Use Local Model", value = False)
    ],
    outputs = "text",
    title="Medical Text Summarization",
    description="Insert a text to summarize"
)

if __name__ == "__main__":
    demo.launch()