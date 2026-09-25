import gradio as gr

def render_home():
    custom_theme = gr.themes.Default(primary_hue="red", neutral_hue="slate")
    
    with gr.Blocks(theme=custom_theme, title="lostAI | ASU") as app:    #title
        with gr.Row():
            gr.Markdown(
                """
                #lostAI: ASU Memorial Union
                **Lost and found, but smarter.**
                """
            )

        #search bar
        with gr.Row():
            search_bar = gr.Textbox(
                show_label=False,
                placeholder="Search lost items (e.g., python homepage.py'blue Hydro Flask', 'car keys', 'AirPods')...",
                scale=5,
                container=False
            )
            search_btn = gr.Button("Search", variant="primary", scale=1)

        with gr.Row():     #action button
            btn_advanced_search = gr.Button("Advanced Search")
            btn_submit_found = gr.Button("Submit a Found Item")

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