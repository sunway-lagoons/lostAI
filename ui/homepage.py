import gradio as gr

#ASU color
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

def render_home():
    custom_theme = gr.themes.Default(
        primary_hue=asu_maroon, 
        secondary_hue=asu_gold, 
        neutral_hue="slate"
    )
    
    with gr.Blocks(theme=custom_theme, title="lostAI | ASU") as app:
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
            # variant="primary" applies the maroon hue
            search_btn = gr.Button("Search", variant="primary", scale=1)

        with gr.Row():
            # variant="secondary" applies the gold hue
            btn_advanced_search = gr.Button("Advanced Search", variant="secondary")
            btn_submit_found = gr.Button("Submit a Found Item", variant="secondary")

        with gr.Column(visible=False) as results_box:
            gr.Markdown("### Search Results")
            results_display = gr.Markdown()

        def show_query(text):
            if not text.strip():
                return gr.update(visible=False), ""
            return gr.update(visible=True), f"Displaying preliminary matches for query: **{text}**"

        search_btn.click(fn=show_query, inputs=search_bar, outputs=[results_box, results_display])
        search_bar.submit(fn=show_query, inputs=search_bar, outputs=[results_box, results_display])

    return app

if __name__ == "__main__":
    demo = render_home()
    demo.launch()