import os
import gradio as gr
from huggingface_hub import InferenceClient


client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

def summarize_text(text):
    """
    Summarize the text
    """
    if text is None:
        return "No text inserted"
    
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
    fn=summarize_text,
    inputs=gr.Textbox(type="text"),
    outputs="text",
    title="Text Summarization (Action Works!)",
    description="Insert a text to summarize"
)

if __name__ == "__main__":
    demo.launch()