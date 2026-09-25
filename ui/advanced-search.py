import gradio as gr

#ASU Color
asu_maroon = gr.themes.Color(
    name="maroon",
    c50="#f5e9ec", c100="#e6c8d1", c200="#d49fae", c300="#c07187", c400="#b14d68",
    c500="#8C1D40", 
    c600="#7a1837", c700="#66132d", c800="#530f24", c900="#450b1d", c950="#2b0510"
)

asu_gold = gr.themes.Color(
    name="gold",
    c50="#fffaf0", c100="#fff2d6", c200="#ffe2a8", c300="#ffd27a", c400="#ffc657",
    c500="#FFC627", 
    c600="#e6b020", c700="#cc9b19", c800="#b38714", c900="#99720f", c950="#664a06"
)

TAGS = [
    "backpack", "water-bottle", "keys", "wallet", 
    "laptop-charger", "airpods-case", "phone", "id-card"
]

def render_advanced_search():
    custom_theme = gr.themes.Default(
        primary_hue=asu_maroon, 
        secondary_hue=asu_gold, 
        neutral_hue="slate"
    )
    
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