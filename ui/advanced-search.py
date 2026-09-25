import gradio as gr

# Placeholder taxonomy
TAGS = ["backpack", "water-bottle", "keys", "wallet", "laptop-charger", "airpods-case", "phone", "id-card"]
ZONES = ["All Locations", "Memorial Union", "Noble Library", "Hayden Library", "Tooker House"]
TIMES = ["Anytime", "Last 24h", "Last 7 days", "Last 30 days"]

def mock_search(term, tags, zone, time, weight, confidence, img):
    if not term and not img:
        return "Please provide a search term or upload an image."
    
    img_status = "Image provided" if img else "No image provided"
    return f"""
    ### Search Executed
    * **Query:** `{term}`
    * **Filters:** {zone} | {time} | Tags: {tags}
    * **Algorithm parameters:** Text Weight: `{weight}%` (Image Weight: `{100-weight}%`) | Min Confidence: `{confidence}`
    * **Image state:** {img_status}
    
    *(Backend DINOv2 and RapidFuzz results would render here based on these constraints.)*
    """

def render_advanced_search():
    custom_theme = gr.themes.Default(primary_hue="red", neutral_hue="slate")
    
    with gr.Blocks(theme=custom_theme, title="Advanced Search") as app:
        gr.Markdown("### Advanced Search: Multimodal Fusion")
        
        with gr.Row():
            # Left Column: Text and Filters
            with gr.Column(scale=2):
                search_term = gr.Textbox(
                    label="Search Term", 
                    placeholder="Provide specific details (e.g., 'cracked screen', 'anime stickers')..."
                )
                
                with gr.Row():
                    adv_tags = gr.Dropdown(label="Tags", choices=TAGS, multiselect=True)
                    adv_zone = gr.Dropdown(label="Spatial Filter", choices=ZONES, value="All Locations")
                    adv_time = gr.Dropdown(label="Temporal Filter", choices=TIMES, value="Last 7 days")
                
                gr.Markdown("#### Algorithm Tuning")
                with gr.Row():
                    text_weight = gr.Slider(
                        label="Text vs. Image Weight (%)", 
                        info="100 = Text Only | 0 = Image Only",
                        minimum=0, maximum=100, value=50, step=10
                    )
                    min_confidence = gr.Slider(
                        label="Min Visual Confidence", 
                        info="Filters out low-probability DINOv2 matches",
                        minimum=0.0, maximum=1.0, value=0.6, step=0.05
                    )
                    
            # Right Column: Image Upload
            with gr.Column(scale=1):
                adv_image = gr.Image(label="Upload Reference Image (Strictly 1 File)", type="filepath")
                
        search_btn = gr.Button("Execute Multi-Vector Search", variant="primary")
        
        with gr.Column() as results_box:
            results_display = gr.Markdown("--- \n*Configure parameters and execute search.*")

        # Wire the button to the dummy function
        search_btn.click(
            fn=mock_search,
            inputs=[search_term, adv_tags, adv_zone, adv_time, text_weight, min_confidence, adv_image],
            outputs=results_display
        )

    return app

if __name__ == "__main__":
    demo = render_advanced_search()
    demo.launch()