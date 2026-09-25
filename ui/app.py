import gradio as gr

# ASU Official Color Definitions
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
    "laptop-charger", "airpods-case", "phone", "id-card",
    "Electronics", "Clothing"
]

asu_theme = gr.themes.Default(
    primary_hue=asu_maroon,
    secondary_hue=asu_gold,
    neutral_hue="slate"
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
    button_primary_text_color="*secondary_500", 
    block_title_text_color="*primary_500",
    slider_color="*secondary_500"
)

# Custom CSS to hide the tab navigation bar and the Gradio footer
css = """
footer { display: none !important; }
.tab-nav { display: none !important; }
"""

def show_query(text):
    if not text.strip():
        return gr.update(visible=False), ""
    return gr.update(visible=True), f"Displaying preliminary matches for query: **{text}**"

def process_submission(title, description, date, location, tags, images):
    num_images = len(images) if images else 0
    if num_images > 4:
        return "⚠️ Error: Please upload a maximum of 4 images."
    if not title or not location:
        return "⚠️ Error: Title and Location are required fields."
    return f"✅ Successfully submitted '{title}'!"

with gr.Blocks(title="lostAI | ASU") as app:
    
    with gr.Tabs() as main_tabs:
        
        # ==========================================
        # TAB 1: HOME PAGE
        # ==========================================
        with gr.Tab("Home", id="home_tab"):
            with gr.Row():
                gr.Markdown(
                    """
                    # lostAI: ASU Memorial Union
                    **Lost and found, but smarter.**
                    """
                )

            with gr.Row():
                search_bar = gr.Textbox(
                    show_label=False,
                    placeholder="Search lost items (e.g., 'blue Hydro Flask', 'car keys', 'AirPods')...",
                    scale=5,
                    container=False
                )
                search_btn = gr.Button("Search", variant="primary", scale=1)

            with gr.Row():
                btn_advanced_search = gr.Button("Advanced Search", variant="secondary")
                btn_submit_found = gr.Button("Submit a Found Item", variant="secondary")

            with gr.Column(visible=False) as results_box:
                gr.Markdown("### Search Results")
                results_display = gr.Markdown()

        # ==========================================
        # TAB 2: ADVANCED SEARCH
        # ==========================================
        with gr.Tab("Advanced Search", id="adv_search_tab"):
            btn_home_from_adv = gr.Button("← Back to Home", variant="secondary", size="sm")
            gr.Markdown("### Advanced Search")
            
            with gr.Row():
                with gr.Column(scale=2):
                    adv_search_term = gr.Textbox(
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
            adv_search_btn = gr.Button("Search", variant="primary")
            adv_results_display = gr.Markdown("--- \n*Results will appear here.*")

        # ==========================================
        # TAB 3: SUBMIT FOUND ITEM
        # ==========================================
        with gr.Tab("Submit a Found Item", id="found_tab"):
            btn_home_from_found = gr.Button("← Back to Home", variant="secondary", size="sm")
            gr.Markdown("### Submit a Lost Item")
            
            with gr.Row():
                submit_title = gr.Textbox(label="Title", placeholder="e.g., Blue Hydro Flask")
                submit_date = gr.Textbox(label="Date", placeholder="YYYY-MM-DD") 
                
            submit_description = gr.Textbox(label="Description", lines=3)
            
            with gr.Row():
                submit_location = gr.Dropdown(
                    choices=["Memorial Union", "Hayden Library", "SDFC", "Computing Commons"], 
                    label="Location"
                )
                submit_tags = gr.Dropdown(
                    choices=TAGS, 
                    label="Tags", 
                    multiselect=True
                )
                
            submit_images = gr.File(file_count="multiple", file_types=["image"], label="Images (Up to 4 files)")
            
            submit_item_btn = gr.Button("Submit Item", variant="primary")
            status_output = gr.Textbox(label="Submission Status", interactive=False)

    # ==========================================
    # BUTTON LINKING & EVENT LOGIC
    # ==========================================
    btn_advanced_search.click(fn=lambda: gr.Tabs(selected="adv_search_tab"), outputs=main_tabs)
    btn_submit_found.click(fn=lambda: gr.Tabs(selected="found_tab"), outputs=main_tabs)
    
    # Return Home logic
    btn_home_from_adv.click(fn=lambda: gr.Tabs(selected="home_tab"), outputs=main_tabs)
    btn_home_from_found.click(fn=lambda: gr.Tabs(selected="home_tab"), outputs=main_tabs)

    search_btn.click(fn=show_query, inputs=search_bar, outputs=[results_box, results_display])
    search_bar.submit(fn=show_query, inputs=search_bar, outputs=[results_box, results_display])

    submit_item_btn.click(
        fn=process_submission,
        inputs=[submit_title, submit_description, submit_date, submit_location, submit_tags, submit_images],
        outputs=[status_output]
    )

if __name__ == "__main__":
    app.launch(theme=asu_theme, css=css)