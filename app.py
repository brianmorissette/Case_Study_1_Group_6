import os
import gradio as gr
from huggingface_hub import InferenceClient
import dotenv

pipe = None
stop_infrence = False

dotenv.load_dotenv()

def summarize_text(
        text,
        use_local_model: bool,
        hf_token
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

            return output[0]["summary_text"]

        except Exception as e:
            return f"Error: {str(e)}"
    
    else:
        try:
            print("[MODE] api")

            if not hf_token:
                return "Please provide a valid Hugging Face API token."

            client = InferenceClient(
                provider="hf-inference",
                api_key=hf_token,
            )

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
    inputs=[
        gr.Textbox(label="Medical Text", lines=15, placeholder="Paste your medical text here..."),
        gr.Checkbox(label="Use Local Model", value=False),
        gr.Textbox(label="Hugging Face Token (required for API mode)", type="password"),
    ],
    outputs = gr.Textbox(lines=15),
    title = "Medical Text Summarization", 
    description = "Insert a medical text to summarize"
)

if __name__ == "__main__":
    demo.launch()