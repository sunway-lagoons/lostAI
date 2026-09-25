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

css = """
footer { display: none !important; }
"""

# ==========================================
# BACKEND MOCK FUNCTIONS
# ==========================================
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

def claim_item(item_name):
    return f"Claim request initiated for: {item_name}. Please proceed to the Information Desk."

def process_bounty(title, location, tags, top_img, bot_img, s1_img, s2_img):
    if not title or not location:
        return "⚠️ Error: Title and Location are required fields."
    
    uploaded_images = [img for img in [top_img, bot_img, s1_img, s2_img] if img is not None]
    
    return f"🚨 REPORT ACTIVATED! '{title}' reported missing with {len(uploaded_images)} reference image(s)."

# ==========================================
# UI CONSTRUCTION
# ==========================================
with gr.Blocks(title="lostAI | ASU") as app:
    
    # ------------------------------------------
    # PAGE 1: HOME (Visible by default)
    # ------------------------------------------
    with gr.Column(visible=True) as home_page:
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
            btn_report_missing = gr.Button("Report a Missing Item", variant="secondary")

        # RECENTLY FOUND ITEMS GRID
        gr.Markdown("### Recently Found Items")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Bag phannypack")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=Fanny+Pack", show_label=False, interactive=False)
                gr.Markdown("Black crossbody bag. Found near SDFC entrance.")
                btn_claim_1 = gr.Button("Claim Item", variant="primary")
                
            with gr.Column():
                gr.Markdown("#### Card wallet")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=Wallet", show_label=False, interactive=False)
                gr.Markdown("Black card holder 'Tommy Hilfiger' Lost 9/25 Found in pod 4 creativity commons")
                btn_claim_2 = gr.Button("Claim Item", variant="primary")
                
            with gr.Column():
                gr.Markdown("#### White beaded ring")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=Ring", show_label=False, interactive=False)
                gr.Markdown("White beaded ring. Found on 2nd floor Noble Library.")
                btn_claim_3 = gr.Button("Claim Item", variant="primary")
                
            with gr.Column():
                gr.Markdown("#### Gold key")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=Gold+Key", show_label=False, interactive=False)
                gr.Markdown("Single gold house key. Found outside Memorial Union.")
                btn_claim_4 = gr.Button("Claim Item", variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("#### AirPod (right)")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=AirPod", show_label=False, interactive=False)
                gr.Markdown("Single right Apple AirPod. Found in Tooker House lobby.")
                btn_claim_5 = gr.Button("Claim Item", variant="primary")
                
            with gr.Column():
                gr.Markdown("#### Black Lenovo charger")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=Charger", show_label=False, interactive=False)
                gr.Markdown("Standard USB-C Lenovo laptop charger.")
                btn_claim_6 = gr.Button("Claim Item", variant="primary")
                
            with gr.Column():
                gr.Markdown("#### Blue HP Computer")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=Laptop", show_label=False, interactive=False)
                gr.Markdown("Blue HP Computer with Corn, Spanish Forks Up, and USGS stickers.")
                btn_claim_7 = gr.Button("Claim Item", variant="primary")
                
            with gr.Column():
                gr.Markdown("#### Airpods")
                gr.Image("https://placehold.co/400x300/8C1D40/FFFFFF/png?text=AirPods+Case", show_label=False, interactive=False)
                gr.Markdown("White Apple AirPods case with both earbuds inside.")
                btn_claim_8 = gr.Button("Claim Item", variant="primary")

        claim_status = gr.Markdown()

        with gr.Column(visible=False) as results_box:
            gr.Markdown("### Search Results")
            results_display = gr.Markdown()

    # ------------------------------------------
    # PAGE 2: ADVANCED SEARCH (Hidden)
    # ------------------------------------------
    with gr.Column(visible=False) as adv_search_page:
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

    # ------------------------------------------
    # PAGE 3: SUBMIT FOUND ITEM (Hidden)
    # ------------------------------------------
    with gr.Column(visible=False) as submit_page:
        btn_home_from_found = gr.Button("← Back to Home", variant="secondary", size="sm")
        gr.Markdown("### Submit a Found Item")
        
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

    # ------------------------------------------
    # PAGE 4: REPORT MISSING ITEM (Hidden)
    # ------------------------------------------
    with gr.Column(visible=False) as report_page:
        btn_home_from_report = gr.Button("← Back to Home", variant="secondary", size="sm")
        gr.Markdown("### 🚨 Report a Missing Item")
        
        with gr.Row():
            report_title = gr.Textbox(label="Title", placeholder="e.g., Missing AirPods Pro")
            
        with gr.Row():
            report_location = gr.Dropdown(
                choices=["Memorial Union", "Hayden Library", "SDFC", "Computing Commons"], 
                label="Last Known Location"
            )
            report_tags = gr.Dropdown(
                choices=TAGS, 
                label="Tags", 
                multiselect=True
            )
            
        gr.Markdown("#### Reference Images")
        with gr.Row():
            report_top = gr.Image(type="filepath", label="Top")
            report_bot = gr.Image(type="filepath", label="Bottom")
        with gr.Row():
            report_s1 = gr.Image(type="filepath", label="Side 1")
            report_s2 = gr.Image(type="filepath", label="Side 2")
        
        report_submit_btn = gr.Button("Post Missing Report", variant="primary")
        report_status = gr.Textbox(label="Report Status", interactive=False)

    # ==========================================
    # BUTTON ROUTING LOGIC
    # ==========================================
    # Helper lists to manage visibility updates efficiently
    all_pages = [home_page, adv_search_page, submit_page, report_page]
    
    def go_to_adv(): return [gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)]
    def go_to_submit(): return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)]
    def go_to_report(): return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)]
    def go_to_home(): return [gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)]

    btn_advanced_search.click(fn=go_to_adv, inputs=None, outputs=all_pages)
    btn_submit_found.click(fn=go_to_submit, inputs=None, outputs=all_pages)
    btn_report_missing.click(fn=go_to_report, inputs=None, outputs=all_pages)
    
    btn_home_from_adv.click(fn=go_to_home, inputs=None, outputs=all_pages)
    btn_home_from_found.click(fn=go_to_home, inputs=None, outputs=all_pages)
    btn_home_from_report.click(fn=go_to_home, inputs=None, outputs=all_pages)

    # ==========================================
    # EVENT LOGIC
    # ==========================================
    btn_claim_1.click(fn=lambda: claim_item("Bag phannypack"), outputs=claim_status)
    btn_claim_2.click(fn=lambda: claim_item("Card wallet"), outputs=claim_status)
    btn_claim_3.click(fn=lambda: claim_item("White beaded ring"), outputs=claim_status)
    btn_claim_4.click(fn=lambda: claim_item("Gold key"), outputs=claim_status)
    btn_claim_5.click(fn=lambda: claim_item("AirPod (right)"), outputs=claim_status)
    btn_claim_6.click(fn=lambda: claim_item("Black Lenovo charger"), outputs=claim_status)
    btn_claim_7.click(fn=lambda: claim_item("Blue HP Computer"), outputs=claim_status)
    btn_claim_8.click(fn=lambda: claim_item("Airpods"), outputs=claim_status)

    search_btn.click(fn=show_query, inputs=search_bar, outputs=[results_box, results_display])
    search_bar.submit(fn=show_query, inputs=search_bar, outputs=[results_box, results_display])

    submit_item_btn.click(
        fn=process_submission,
        inputs=[submit_title, submit_description, submit_date, submit_location, submit_tags, submit_images],
        outputs=[status_output]
    )
    
    report_submit_btn.click(
        fn=process_bounty,
        inputs=[report_title, report_location, report_tags, report_top, report_bot, report_s1, report_s2],
        outputs=[report_status]
    )

if __name__ == "__main__":
    app.launch(theme=asu_theme, css=css)