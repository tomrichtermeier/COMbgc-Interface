from modules import (
    combgc_table_ui, combgc_table_server,
    combgc_general_statistics_server, combgc_general_statistics_ui, 
    combgc_barplot_ui, combgc_barplot_server, 
    combgc_taxonomy_ui, combgc_taxonomy_server,
    taxonomy_stacked_bar_ui, taxonomy_stacked_bar_server,
    filter_data
    )
from plots import preprocess_taxonomy_column
from shiny import App, Inputs, Outputs, Session, reactive, ui, render

import shinyswatch
from pathlib import Path
import pandas as pd

# Load data once to define product_classes
data_path = "filtered_bgcs.tsv"
data = pd.read_csv(data_path, sep="\t")
# Extract unique product classes for the checkbox group
product_classes = sorted({item for entry in data["Product_class"].dropna() for item in entry.split(", ")})

#################
# UI: user interface function
#################
app_ui = ui.page_navbar(
    shinyswatch.theme.minty(),
    combgc_table_ui("tab1"),
    combgc_general_statistics_ui("tab2"),
    combgc_barplot_ui("tab3"), 
    taxonomy_stacked_bar_ui("tab4"),
    combgc_taxonomy_ui("tab5"), 
    # Sidebar
    sidebar=ui.sidebar(
        # Add logo
        ui.img(src="com-bgc-logo.png", style="width:200px;"),
        ui.a(dict(href="https://github.com/tomrichtermeier/COMbgc-Interface"), "COMbgc documentation"),
        # Upload file in TSV format
        ui.p("Choose a file to upload:"),
        ui.input_file("combgc_user_tsv", label="", accept=[".tsv"]),
        
        ui.p(),
        ui.HTML("<h4 style='color: #595959; font-size: 18px; font-weight: bold; margin-bottom: -5px;'>Select Prediction Tool</h4>"),
        ui.input_checkbox_group(
            "tool_selection", 
            None, 
            choices=["deepBGC", "GECCO", "antiSMASH", "All"], 
            selected=["deepBGC", "GECCO", "antiSMASH"],
        ),

        ui.p(),  
        ui.HTML("<h4 style='color: #595959; font-size: 18px; font-weight: bold; margin-bottom: -5px;'>Filter by BGC Length</h4>"),
        ui.row(
        ui.column(6, ui.input_numeric(
            "bgc_length_min",
            "Minimum:",
            value=3000,
            step=1,
        )),
        ui.column(6, ui.input_numeric(
            "bgc_length_max",
            "Maximum:",
            value=1000000,  # Set to the maximum value in your data
            step=1,
        ))
        ),
        
        ui.HTML("<h4 style='color: #595959; font-size: 18px; font-weight: bold; margin-bottom: -5px;'>Select Product Class</h4>"),
        ui.input_action_button(
            "toggle_product_classes",
            "Select/Unselect all",
            class_="btn btn-outline-dark",
            style="font-size: 12px; padding: 2px 0px; display: inline-block;"
        ),
        ui.input_checkbox_group("product_class", None, choices=product_classes, selected=product_classes),
        ui.p(""),
        width="300px"
    ),
    title="COMbgc",
    id="tabs",
)



def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc()
    def filtered_data() -> pd.DataFrame:
        file_infos = input.combgc_user_tsv()
        if not file_infos:
            return None

        for file_info in file_infos:
            out_str = file_info["datapath"]
            data = pd.read_csv(out_str, sep="\t")
        
        selected_tools = input.tool_selection()
        deepBGC_selected = "deepBGC" in selected_tools
        GECCO_selected = "GECCO" in selected_tools
        antiSMASH_selected = "antiSMASH" in selected_tools
        all_selected = "All" in selected_tools

        selected_product_classes = input.product_class()
        bgc_length_min = input.bgc_length_min() or 0
        bgc_length_max = input.bgc_length_max() or float("inf")

        # Apply the filter_data function to filter based on sidebar inputs
        data = filter_data(data, deepBGC_selected, GECCO_selected, antiSMASH_selected, all_selected, selected_product_classes, bgc_length_min, bgc_length_max)
        data["mmseqs_lineage_contig"] = data["mmseqs_lineage_contig"].astype(str).fillna("")
        data = data.drop(columns="identifier")
        return data
    

    @reactive.Effect
    @reactive.event(input.tool_selection)
    def toggle_all_behavior():  # if on is toggled all other are automatically toggled of
        selected_tools = input.tool_selection()
        if "All" in selected_tools and len(selected_tools) > 1:
            session.send_input_message("tool_selection", {"value": ["All"]})
        elif "All" not in selected_tools and not selected_tools:
            session.send_input_message("tool_selection", {"value": ["deepBGC", "GECCO", "antiSMASH"]})


    @reactive.Effect
    @reactive.event(input.toggle_product_classes)
    def on_toggle_product_classes():
        # Get the list of all product classes
        all_product_classes = product_classes
        current_selection = input.product_class() or []
        # Toggle selection based on the current state
        if set(current_selection) == set(all_product_classes):
            new_selection = [] # If all are selected, unselect all
        else:
            new_selection = all_product_classes # Otherwise, select all
        session.send_input_message("product_class", {"value": new_selection})


    combgc_table_server(id="tab1", df=filtered_data)
    combgc_general_statistics_server(id="tab2", df=filtered_data)
    combgc_barplot_server(id="tab3", df=filtered_data)
    taxonomy_stacked_bar_server(id="tab4", df=filtered_data)
    combgc_taxonomy_server(id="tab5", df=filtered_data)

    
# Add path to logo
www_dir = Path(__file__).parent / ""  # Change path to the directory where images should be found
app = App(app_ui, server, static_assets=www_dir)


