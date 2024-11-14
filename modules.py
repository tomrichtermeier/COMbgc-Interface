import pandas as pd
from typing import Callable
from shiny import Inputs, Outputs, Session, module, render, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px


from plots import (
    boxplot_product_classes, 
    stacked_bars_product_classes, 
    create_venn, 
    plot_combgc_sankey, 
    preprocess_taxonomy_column, 
    stacked_bars_taxonomy,
    scatter_bgc_contig_classes
    )

###########################################
#SHINY VERSION == 0.7.1
###########################################

###########################################
#       TABLE
###########################################
@module.ui
def combgc_table_ui():
    return ui.nav_panel(
        "Table",  # Name of the tab
        # download rows selected: table tab
        ui.p("Download only the selected rows:"),
        ui.row(
            ui.card(
                ui.download_button("download_combgc_table_rows", "Download 'combgc_selected_rows.tsv'", class_="btn btn-info")
            )
        ),
        ui.p("Rows selected by user:", style="font-size: 20px;"),
        ui.output_text("combgc_table_rows", inline=True),
        ui.output_data_frame("combgc_table_dataframe")
    )


@module.server
def combgc_table_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: Callable[[], pd.DataFrame],
    ):
    selected_rows = reactive.Value([])  # Store selected rows
    
    @render.data_frame
    def combgc_table_dataframe():
        """"
        AMPCOMBI: render dataframe in a table
        """
        if isinstance(df(), pd.DataFrame):
            # render grid table
            data_grid = render.DataGrid(df(),                                           
                                        row_selection_mode="multiple", 
                                        width="100%", 
                                        height="1000px",
                                        filters=True)
            return data_grid
        else:
            return None

    @output
    @render.text
    def combgc_table_rows():
        """
        COMbgc: prints the row numbers selected by user
        """
        selected = input.combgc_table_dataframe_selected_rows() or selected_rows.get()
        l = ", ".join(str(i) for i in selected)
        return l

    @output
    @render.download(filename=lambda: "combgc_table_selected_rows.tsv")
    async def download_combgc_table_rows():
        indices = list(input.combgc_table_dataframe_selected_rows() or selected_rows.get())
        selected_rows_data = df().iloc[indices]
        yield selected_rows_data.to_csv(sep="\t", index=False)





###########################################
#      BOXPLOT
###########################################
@module.ui
def combgc_general_statistics_ui():
    return ui.nav_panel(
        "General Statistics",  # Name of the tab
        #ui.p("Select the minimum amount of bgcs for the category to be displayed:"),
        output_widget("venn_diagram"),
        output_widget("boxplot"),
        ui.input_slider("boxplot_threshold", "Select the minimum amount of bgcs for the product class to be displayed:", min=1, max=50, value=1, step=1),
        ui.p(""),
        ui.row(
            ui.card(
                ui.download_button("download_data", "Download 'combgc_table_filtered.tsv'", class_="btn btn-info")
            )
        ),
        ui.output_data_frame("combgc_table"),
    )


@module.server
def combgc_general_statistics_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: Callable[[], pd.DataFrame],
    ):
    @output
    @render_widget
    def venn_diagram():
        data = df()  # Reactive data retrieval

        if data is not None and not data.empty:
            return create_venn(data)
        return None

    @output
    @render_widget
    def boxplot():
        number_plots = input.boxplot_threshold()  # Get the threshold from the slider
        data = df()  # Get the filtered data from reactive function

        if data is not None and not data.empty:
            return boxplot_product_classes(data, number_plots)  # Pass the correct threshold
        return None
    

    @render.data_frame
    def combgc_table():
        return render.DataTable(df(), width="100%")
        
    @render.download(
    filename=lambda: "combgc_table_filtered.tsv"
    )
    def download_data():
        filtered_data = df()
        yield filtered_data.to_csv(sep="\t", index=False)





###########################################
#        PRODUCT CLASS -- BARS
###########################################
@module.ui
def combgc_barplot_ui():
    return ui.nav_panel(
        "Class Distribution",
        output_widget("barplot_output"),
        ui.p(""),
        output_widget("scatter_output"),
        ui.p(""),
        ui.row(
            ui.card(
                ui.download_button("download_data", "Download 'combgc_table_filtered.tsv'", class_="btn btn-info")
            )
        ),
        ui.output_data_frame("combgc_table")
    )

@module.server
def combgc_barplot_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: Callable[[], pd.DataFrame],
    ):
    @output
    @render_widget
    def barplot_output():
        data = df()  # Call the reactive function to get the actual DataFrame
        if data is not None and not data.empty:
            return stacked_bars_product_classes(data)  # Pass the DataFrame to the plot function
        return None
    
    @output
    @render_widget
    def scatter_output():
        data = df()  # Call the reactive function to get the actual DataFrame
        if data is not None and not data.empty:
            return scatter_bgc_contig_classes(data)  # Pass the DataFrame to the plot function
        return None


    @render.data_frame
    def combgc_table():
        return render.DataTable(df(), width="100%")
        
    @render.download(
    filename=lambda: "combgc_table_filtered.tsv"
    )
    def download_data():
        filtered_data = df()
        yield filtered_data.to_csv(sep="\t", index=False)




###########################################
#      Taxonomy
###########################################

@module.ui
def taxonomy_stacked_bar_ui():
    return ui.nav_panel(
        "Taxonomy Distribution",
        ui.input_select("taxonomy_level", "Select Taxonomy Level:", choices=["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]),
        ui.output_ui("taxonomy_options_ui"),  # Placeholder for dynamic checkbox options
        output_widget("taxonomy_stacked_bar"),
        ui.p(""),
        ui.row(
            ui.card(
                ui.download_button("download_data", "Download 'combgc_table_filtered.tsv'", class_="btn btn-info")
            )
        ),
        ui.output_data_frame("combgc_table"),
    )

@module.server
def taxonomy_stacked_bar_server(input: Inputs, output: Outputs, session: Session, df: Callable[[], pd.DataFrame]):
    @output
    @render_widget
    def taxonomy_stacked_bar():
        data = df()
        if data is not None and not data.empty:
            #data["sample_id"] = data["sample_id"].str.split("-").str[0]
            data = preprocess_taxonomy_column(data, column_name="mmseqs_lineage_contig")  # Preprocess if not already done
            taxonomy_level = input.taxonomy_level()
            selected_options = input.taxonomy_options()  # Get selected options from the checkbox
            if selected_options:
                selected_options = [opt.replace("_", " ") for opt in selected_options]
                data = data[data[taxonomy_level].isin(selected_options)]

            
            return stacked_bars_taxonomy(data, taxonomy_level)
        return None
    
    @output
    @render.data_frame
    def combgc_table():
        data = df()
        if data is not None and not data.empty:
            taxonomy_level = input.taxonomy_level()
            selected_options = input.taxonomy_options()  # Get selected options from the checkbox
            if selected_options:
                selected_options = [opt.replace("_", " ") for opt in selected_options]
                data = data[data[taxonomy_level].isin(selected_options)]
        return render.DataTable(data, width="100%")
        
    @render.download(
    filename=lambda: "combgc_table_filtered.tsv"
    )
    def download_data():
        data = df()
        if data is not None and not data.empty:
            taxonomy_level = input.taxonomy_level()
            selected_options = input.taxonomy_options()  # Get selected options from the checkbox
            if selected_options:
                data = data[data[taxonomy_level].isin(selected_options)]
        yield data.to_csv(sep="\t", index=False)


    @output
    @render.ui
    def taxonomy_options_ui():
        taxonomy_level = input.taxonomy_level()

        # Get the filtered data and apply the taxonomy preprocessing
        data = df()
        if data is not None and taxonomy_level in data.columns:
            unique_values = sorted(data[taxonomy_level].dropna().unique())
            return ui.input_checkbox_group("taxonomy_options", "Select Specific Taxonomy Options:", choices=unique_values, selected=unique_values)
        else:
            print(f"Warning: Taxonomy level '{taxonomy_level}' not found in data columns.")
        
        # Default empty checkbox if no data or column is available
        return ui.input_checkbox_group("taxonomy_options", "Select Specific Taxonomy Options:", choices=[])


# ########################################
#      Sankey
###########################################
@module.ui
def combgc_taxonomy_ui():
    return  ui.nav_panel(
        "Sankey",
                ui.p(
                    {"style": "font-size: 20px;"},
                    """
                    Enter cluster ID here to filter plot
                    """
                    ),
                ui.input_numeric("clusters_id_tax", "", value=None),
                output_widget("combgc_sankey_plot"), 
                {"style": "font-size: 15px;"},
                "The sankey plot showing the taxonomic lineage is rendered in a new tab in which the user can interactively adjust.", 
    )

@module.server
def combgc_taxonomy_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    df: Callable[[], pd.DataFrame],
):
    @output
    @render_widget
    def combgc_sankey_plot():
        data = df()
        if data is not None and not data.empty:
            # Check if the mmseqs_contig_lineage column exists and has only NaN values
            if "mmseqs_contig_lineage" in data.columns and data["mmseqs_contig_lineage"].isna().all():
                raise ValueError("Error: No values found in mmseqs_contig_lineage column.")
            return plot_combgc_sankey(data)
        return None






###########################################
#      FILTER DATA
###########################################
def filter_data(df, deepBGC_selected, GECCO_selected, antiSMASH_selected, all_selected, selected_product_classes, bgc_length_min, bgc_length_max):
    # Initialize a base mask with False values, aligned with the DataFrame index
    base_mask = pd.Series([False] * len(df), index=df.index)
    
    # Apply all_selected condition first
    if all_selected:
        base_mask |= (df["deepBGC"] == "Yes") & (df["GECCO"] == "Yes") & (df["antiSMASH"] == "Yes")
    else:
        # Apply individual selection criteria
        if deepBGC_selected:
            base_mask |= (df["deepBGC"] == "Yes")
        if GECCO_selected:
            base_mask |= (df["GECCO"] == "Yes")
        if antiSMASH_selected:
            base_mask |= (df["antiSMASH"] == "Yes")

    # Product class filtering - create a boolean mask based on selected product classes
    if selected_product_classes:
        class_mask = df["Product_class"].apply(lambda x: any(item in selected_product_classes for item in x.split(", ")) if pd.notna(x) else False)
        class_mask = class_mask.astype(bool)  # Ensure mask is strictly boolean
        base_mask &= class_mask
    
    # Convert BGC_length to numeric and filter by min and max values
    length_mask = (df["BGC_length"] >= bgc_length_min) & (df["BGC_length"] <= bgc_length_max)
    length_mask = length_mask.fillna(False).astype(bool)  # Ensure no NaN values, strictly boolean
    base_mask &= length_mask

    # Return filtered DataFrame
    return df[base_mask]


