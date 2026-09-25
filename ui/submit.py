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

# Updated function to handle 4 separate image inputs
def process_submission(title, description, date, location, tags, top_img, bot_img, s1_img, s2_img):
    if not title or not location:
        return "⚠️ Error: Title and Location are required fields."
    
    # Optional: count how many images were actually uploaded
    uploaded_images = [img for img in [top_img, bot_img, s1_img, s2_img] if img is not None]
    
    return f"✅ Successfully submitted '{title}' with {len(uploaded_images)} image(s)!"

# 3. Apply the theme in Blocks
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
        
    gr.Markdown("### Image Uploads")
    
    # 4 separate image boxes arranged in a 2x2 grid
    with gr.Row():
        top_image = gr.Image(type="filepath", label="Top")
        bottom_image = gr.Image(type="filepath", label="Bottom")
    with gr.Row():
        side1_image = gr.Image(type="filepath", label="Side 1")
        side2_image = gr.Image(type="filepath", label="Side 2")
    
    submit_btn = gr.Button("Submit Item", variant="primary")
    status_output = gr.Textbox(label="Submission Status", interactive=False)
    
    # Make sure to pass all 4 image components to the inputs list
    submit_btn.click(
        fn=process_submission,
        inputs=[title, description, date, location, tags, top_image, bottom_image, side1_image, side2_image],
        outputs=[status_output]
    )

if __name__ == "__main__":
    # 4. Pass the custom ASU theme directly into the launch method
    lost_found_ui.launch(theme=asu_theme)