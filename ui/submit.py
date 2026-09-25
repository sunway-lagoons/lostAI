import gradio as gr

# 1. Define the ASU colors as Gradio Color objects with light-to-dark shades
asu_maroon = gr.themes.Color(
    name="maroon",
    c50="#f5e9ec", c100="#e6c8d1", c200="#d49fae", c300="#c07187", c400="#b14d68",
    c500="#8C1D40", # Official ASU Maroon
    c600="#7a1837", c700="#66132d", c800="#530f24", c900="#450b1d", c950="#2b0510"
)

asu_gold = gr.themes.Color(
    name="gold",
    c50="#fffaf0", c100="#fff2d6", c200="#ffe2a8", c300="#ffd27a", c400="#ffc657",
    c500="#FFC627", # Official ASU Gold
    c600="#e6b020", c700="#cc9b19", c800="#b38714", c900="#99720f", c950="#664a06"
)

# 2. Build the custom theme and force the button colors
asu_theme = gr.themes.Default(
    primary_hue=asu_maroon,
    secondary_hue=asu_gold,
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
    button_primary_text_color="*secondary_500", # Gold text on Maroon button
    block_title_text_color="*primary_500",
    slider_color="*secondary_500"
)

def process_submission(title, description, date, location, tags, images):
    num_images = len(images) if images else 0
    if num_images > 4:
        return "⚠️ Error: Please upload a maximum of 4 images."
    if not title or not location:
        return "⚠️ Error: Title and Location are required fields."
    return f"✅ Successfully submitted '{title}'!"

# 3. Apply the theme in Blocks (notice theme is removed from here for Gradio 6.0)
with gr.Blocks() as lost_found_ui:
    gr.Markdown("# 🔱 Submit a Lost Item")
    
    with gr.Row():
        title = gr.Textbox(label="Title", placeholder="e.g., Blue Hydro Flask")
        date = gr.Textbox(label="Date", placeholder="YYYY-MM-DD") 
        
    description = gr.Textbox(label="Description", lines=3)
    
    with gr.Row():
        location = gr.Dropdown(
            choices=["Memorial Union", "Hayden Library", "SDFC", "Computing Commons"], 
            label="Location"
        )
        tags = gr.Dropdown(
            choices=["Electronics", "Water Bottles", "Keys", "Clothing", "Wallet/ID"], 
            label="Tags", 
            multiselect=True
        )
        
    images = gr.File(file_count="multiple", file_types=["image"], label="Images (Up to 4 files)")
    
    submit_btn = gr.Button("Submit Item", variant="primary")
    status_output = gr.Textbox(label="Submission Status", interactive=False)
    
    submit_btn.click(
        fn=process_submission,
        inputs=[title, description, date, location, tags, images],
        outputs=[status_output]
    )

if __name__ == "__main__":
    # 4. Pass the custom ASU theme directly into the launch method
    lost_found_ui.launch(theme=asu_theme)