import gradio as gr

TAGS = [
    "backpack", "water-bottle", "keys", "wallet", 
    "laptop-charger", "airpods-case", "phone", "id-card"
]

def render_advanced_search():
    custom_theme = gr.themes.Default(primary_hue="red", neutral_hue="slate")
    
    with gr.Blocks(theme=custom_theme) as app:
        gr.Markdown("### Advanced Search")
        
        with gr.Row():
            with gr.Column(scale=2):
                search_term = gr.Textbox(
                    label="Search Term", 
                    placeholder="Enter item details..."
                )
                adv_tags = gr.Dropdown(
                    label="Tags", 
                    choices=TAGS, 
                    multiselect=True
                )
                
            with gr.Column(scale=1):
                adv_image = gr.Image(
                    label="Upload Reference Image", 
                    type="filepath"
                )
                
        search_btn = gr.Button("Search", variant="primary")
        results_display = gr.Markdown("--- \n*Results will appear here.*")

    return app

if __name__ == "__main__":
    demo = render_advanced_search()
    demo.launch()