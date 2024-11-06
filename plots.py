import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



###########################################
#       BOXPLOT
############################################
##### Plots all product classes ######
def boxplot_product_classes(table, number_plots):
    """
    Generates a boxplot of BGC lengths by Product Class with a dynamic threshold for number of classes.
    """
    filtered_bgcs = table
    
    # Keep the full product class entries without splitting them
    filtered_bgcs["Product_class"] = filtered_bgcs["Product_class"].apply(lambda x: x.strip())
    
    # Filter out classes that have less count than `number_plots`
    class_counts = filtered_bgcs["Product_class"].value_counts()
    valid_classes = class_counts[class_counts > number_plots].index
    
    # Define ascending order for product classes
    class_order = class_counts.loc[valid_classes].sort_values(ascending=False).index
    
    # Filter the DataFrame based on valid product classes
    filtered_bgcs = filtered_bgcs[filtered_bgcs["Product_class"].isin(valid_classes)]
    
    # Create the boxplot using Plotly
    fig = px.box(filtered_bgcs, 
                 x="Product_class", 
                 y="BGC_length", 
                 title="BGC Length by Product Class (log scale)",
                 labels={"Product_class": "Product Class", "BGC_length": "BGC Length"},
                 hover_data=["sample_id"])

    # Add log scale and sort by class count
    fig.update_layout(yaxis_type="log", xaxis={"categoryorder": "array", "categoryarray": class_order})
    fig.update_xaxes(tickangle=-35)

    return fig






###########################################
#       STACKED BARS
###########################################

##### Only takes on in the product class #####
def stacked_bars_product_classes(table):
    filtered_bgcs = table.copy()
    filtered_bgcs["sample_id"] = filtered_bgcs["sample_id"].str.split("-").str[0]

    # Extract sample name from the bgc identifier
    filtered_bgcs["sample_name"] = filtered_bgcs["sample_id"].str.split("_").str[0]

    # Count occurrences of each "Product_class" grouped by "sample_name"
    product_class_counts = filtered_bgcs.groupby(["sample_name", "Product_class"]).size().unstack(fill_value=0).reset_index()

    # Melt the dataframe to long format for easier plotting with Plotly
    product_class_counts_melted = product_class_counts.melt(id_vars="sample_name", var_name="First_Product_class", value_name="Count")
    
    # Create the stacked bar plot using Plotly
    fig = px.bar(product_class_counts_melted, 
                 x="sample_name", 
                 y="Count", 
                 color="First_Product_class", 
                 title="Stacked Bar Plot of Product Class Counts per Sample",
                 labels={"sample_name": "Sample", "Count": "Count"},
                 barmode="stack")
    
    fig.update_layout(
        width=1200,  # Set the width (in pixels)
        height=800  # Set the height (in pixels)
    )
    
    fig.update_xaxes(tickangle=-90)
    
    return fig  # Return the figure object, do not call fig.show()






###########################################
#      VENN DIAGRAM
###########################################

def create_venn(table):
    filtered_bgcs = table
    fig = go.Figure()

    # Count occurrences based on the specified conditions
    counts = {
        "deepbgc_count": ((filtered_bgcs["deepBGC"] == "Yes") & 
                        (filtered_bgcs["GECCO"].isnull()) & 
                        (filtered_bgcs["antiSMASH"].isnull())).sum(),
        "gecco_count": ((filtered_bgcs["deepBGC"].isnull()) & 
                        (filtered_bgcs["GECCO"] == "Yes") & 
                        (filtered_bgcs["antiSMASH"].isnull())).sum(),
        "antismash_count": ((filtered_bgcs["deepBGC"].isnull()) & 
                            (filtered_bgcs["GECCO"].isnull()) & 
                            (filtered_bgcs["antiSMASH"] == "Yes")).sum(),
        "deepbgc_gecco_count": ((filtered_bgcs["deepBGC"] == "Yes") & 
                                (filtered_bgcs["GECCO"] == "Yes") & 
                                (filtered_bgcs["antiSMASH"].isnull())).sum(),
        "deepbgc_antismash_count": ((filtered_bgcs["deepBGC"] == "Yes") & 
                                    (filtered_bgcs["GECCO"].isnull()) & 
                                    (filtered_bgcs["antiSMASH"] == "Yes")).sum(),
        "antismash_gecco_count": ((filtered_bgcs["deepBGC"].isnull()) & 
                                (filtered_bgcs["GECCO"] == "Yes") & 
                                (filtered_bgcs["antiSMASH"] == "Yes")).sum(),
        "all_count": ((filtered_bgcs["antiSMASH"] == "Yes") & 
                    (filtered_bgcs["deepBGC"] == "Yes") & 
                    (filtered_bgcs["GECCO"] == "Yes")).sum()
    }

    # Create scatter trace of text labels with values
    fig.add_trace(go.Scatter(
        x=[0.45, 2.55, 1.5, 1.5, 2.25, 0.75, 1.5, 1.5, -0.1, 3.1],
        y=[0.6 , 0.6 , 2.5, 0.5, 1.75, 1.75, 1.35, 3.1, 0.25, 0.25],
        text=[
            f"\n{counts["deepbgc_count"]}",                   # Left circle only (deepBGC)
            f"\n{counts["antismash_count"]}",                 # Right circle only (antiSMASH)
            f"\n{counts["gecco_count"]}",                     # Top circle only (GECCO)
            f"\n{counts["deepbgc_antismash_count"]}",           # deepBGC & antiSMASH
            f"\n{counts["antismash_gecco_count"]}",             # antiSMASH & GECCO
            f"\n{counts["deepbgc_gecco_count"]}",               # deepBGC & GECCO
            f"\n{counts["all_count"]}",                       # all three
            f"GECCO",
            f"deepBGC",
            f"antiSMASH"
        ],
        mode="text",
        textfont=dict(
            color="black",
            size=18,
            family="Arial",
        )
    ))
    # deepBGC circle
    fig.add_shape(
        type="circle", 
        line_color="black", 
        fillcolor="blue", 
        x0=0, y0=0, x1=2, y1=2
    )
    # antiSMASH circle
    fig.add_shape(
        type="circle", 
        line_color="black", 
        fillcolor="red", 
        x0=1, y0=0, x1=3, y1=2
    )  
    # GECCO circle
    fig.add_shape(
        type="circle", 
        line_color="black", 
        fillcolor="green", 
        x0=0.5, y0=1, x1=2.5, y1=3
    )
    # Update axes properties
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False
    )
    # Update shape opacity
    fig.update_shapes(
        opacity=0.3,
        xref="x",
        yref="y"
    )
    # Update layout 
    fig.update_layout(
        title="Amount of BGC Detected by Prediction Tools",
        title_font=dict(size=20),
        margin=dict(l=20, r=20, b=100),
        height=450, width=450,
        plot_bgcolor="white",
        yaxis_scaleanchor="x",  # aspect ratio equal
    )
    return fig







###########################################
#      Taxonomy
###########################################

def preprocess_taxonomy_column(data, column_name="taxonomy"):
    """
    Extracts and creates separate columns for each taxonomy level from a combined string.
    """
    taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
    split_taxonomy = data[column_name].str.split(";", expand=True)

    # Create separate columns for each level
    for i, level in enumerate(taxonomy_levels):
        if i < split_taxonomy.shape[1]:  # Check if the column exists
            data[level] = split_taxonomy[i].str.split("_", n=1).str[1]  # Correctly use n=1

    return data


def stacked_bars_taxonomy(data, taxonomy_level):
    """
    Generate a stacked bar plot for taxonomies at the specified level.
    """
    if taxonomy_level not in data.columns:
        raise ValueError(f"Taxonomy level '{taxonomy_level}' not found in the data columns.")
    
    data_copy = data.copy()
    data_copy["sample_id"] = data_copy["sample_id"].str.split("-").str[0]
    grouped_data = data_copy.groupby(["sample_id", taxonomy_level]).size().reset_index(name="Count")

    fig = px.bar(
        grouped_data,
        x="sample_id",  # Replace with the column representing the x-axis
        y="Count",   # Replace with the column representing the y-axis
        color=taxonomy_level,
        title=f"Stacked Bar Plot for Taxonomy Level: {taxonomy_level}"
    )    
    fig.update_layout(
        width=1000,  # Set the width (in pixels)
        height=800  # Set the height (in pixels)
    )
    
    fig.update_xaxes(tickangle=-90)

    fig.update_layout(barmode="stack")
    return fig



def plot_combgc_sankey(filtered):
    # set up data and layout required by sankey plots
    data = [
        {
        "type": "sankey", 
        "domain": {"x": [0, 1], "y": [0, 1]}, 
        "orientation": "h", 
        "valueformat": ".0f", 
        "valuesuffix": "TWh", 
        "node": {
            "pad": 15, 
            "thickness": 15, 
            "line": {"color": "black", "width": 0.5}, 
            #"label": ["Agricultural "waste"", "Bio-conversion", "Liquid", "Losses", "Solid", "Gas", "Biofuel imports", "Biomass imports", "Coal imports", "Coal", "Coal reserves", "District heating", "Industry", "Heating and cooling - commercial", "Heating and cooling - homes", "Electricity grid", "Over generation / exports", "H2 conversion", "Road transport", "Agriculture", "Rail transport", "Lighting & appliances - commercial", "Lighting & appliances - homes", "Gas imports", "Ngas", "Gas reserves", "Thermal generation", "Geothermal", "H2", "Hydro", "International shipping", "Domestic aviation", "International aviation", "National navigation", "Marine algae", "Nuclear", "Oil imports", "Oil", "Oil reserves", "Other waste", "Pumped heat", "Solar PV", "Solar Thermal", "Solar", "Tidal", "UK land based bioenergy", "Wave", "Wind"], 
            #"color": ["rgba(31, 119, 180, 0.8)", "rgba(255, 127, 14, 0.8)", "rgba(44, 160, 44, 0.8)", "rgba(214, 39, 40, 0.8)", "rgba(148, 103, 189, 0.8)", "rgba(140, 86, 75, 0.8)", "rgba(227, 119, 194, 0.8)", "rgba(127, 127, 127, 0.8)", "rgba(188, 189, 34, 0.8)", "rgba(23, 190, 207, 0.8)", "rgba(31, 119, 180, 0.8)", "rgba(255, 127, 14, 0.8)", "rgba(44, 160, 44, 0.8)", "rgba(214, 39, 40, 0.8)", "rgba(148, 103, 189, 0.8)", "rgba(140, 86, 75, 0.8)", "rgba(227, 119, 194, 0.8)", "rgba(127, 127, 127, 0.8)", "rgba(188, 189, 34, 0.8)", "rgba(23, 190, 207, 0.8)", "rgba(31, 119, 180, 0.8)", "rgba(255, 127, 14, 0.8)", "rgba(44, 160, 44, 0.8)", "rgba(214, 39, 40, 0.8)", "rgba(148, 103, 189, 0.8)", "rgba(140, 86, 75, 0.8)", "rgba(227, 119, 194, 0.8)", "rgba(127, 127, 127, 0.8)", "rgba(188, 189, 34, 0.8)", "rgba(23, 190, 207, 0.8)", "rgba(31, 119, 180, 0.8)", "rgba(255, 127, 14, 0.8)", "rgba(44, 160, 44, 0.8)", "rgba(214, 39, 40, 0.8)", "rgba(148, 103, 189, 0.8)", "magenta", "rgba(227, 119, 194, 0.8)", "rgba(127, 127, 127, 0.8)", "rgba(188, 189, 34, 0.8)", "rgba(23, 190, 207, 0.8)", "rgba(31, 119, 180, 0.8)", "rgba(255, 127, 14, 0.8)", "rgba(44, 160, 44, 0.8)", "rgba(214, 39, 40, 0.8)", "rgba(148, 103, 189, 0.8)", "rgba(140, 86, 75, 0.8)", "rgba(227, 119, 194, 0.8)", "rgba(127, 127, 127, 0.8)"]
            }, 
        "link": {
            #"source": [0, 1, 1, 1, 1, 6, 7, 8, 10, 9, 11, 11, 11, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 23, 25, 5, 5, 5, 5, 5, 27, 17, 17, 28, 29, 2, 2, 2, 2, 2, 2, 2, 2, 34, 24, 35, 35, 36, 38, 37, 39, 39, 40, 40, 41, 42, 43, 43, 4, 4, 4, 26, 26, 26, 44, 45, 46, 47, 35, 35], 
            #"target": [1, 2, 3, 4, 5, 2, 4, 9, 9, 4, 12, 13, 14, 16, 14, 17, 12, 18, 19, 13, 3, 20, 21, 22, 24, 24, 13, 3, 26, 19, 12, 15, 28, 3, 18, 15, 12, 30, 18, 31, 32, 19, 33, 20, 1, 5, 26, 26, 37, 37, 2, 4, 1, 14, 13, 15, 14, 42, 41, 19, 26, 12, 15, 3, 11, 15, 1, 15, 15, 26, 26], 
            #"value": [124.729, 0.597, 26.862, 280.322, 81.144, 35, 35, 11.606, 63.965, 75.571, 10.639, 22.505, 46.184, 104.453, 113.726, 27.14, 342.165, 37.797, 4.412, 40.858, 56.691, 7.863, 90.008, 93.494, 40.719, 82.233, 0.129, 1.401, 151.891, 2.096, 48.58, 7.013, 20.897, 6.242, 20.897, 6.995, 121.066, 128.69, 135.835, 14.458, 206.267, 3.64, 33.218, 4.413, 14.375, 122.952, 500, 139.978, 504.287, 107.703, 611.99, 56.587, 77.81, 193.026, 70.672, 59.901, 19.263, 19.263, 59.901, 0.882, 400.12, 46.477, 525.531, 787.129, 79.329, 9.452, 182.01, 19.013, 289.366, 100, 100] 
            #"color": ["rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(33,102,172,0.35)", "rgba(178,24,43,0.35)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "rgba(0,0,96,0.2)", "lightgreen", "goldenrod"] 
            #"label": ["stream 1", "", "", "", "stream 1", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "stream 1", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Old generation plant (made-up)", "New generation plant (made-up)", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
            }
        }
        ]

    df_amp = filtered

    # grab the contig GTDB classifications
    df_amp[["kingdom", "phylum", "class", "order", "family", "genus", "specie"]] = df_amp["mmseqs_lineage_contig"].str.split(";", expand=True)
    # remove the prefix from each column
    df_amp["kingdom"] = df_amp["kingdom"].str.replace("d_", "")
    df_amp["phylum"] = df_amp["phylum"].str.replace("p_", "")
    df_amp["class"] = df_amp["class"].str.replace("c_", "")
    df_amp["order"] = df_amp["order"].str.replace("o_", "")
    df_amp["family"] = df_amp["family"].str.replace("f_", "")
    df_amp["genus"] = df_amp["genus"].str.replace("g_", "")
    df_amp["specie"] = df_amp["specie"].str.replace("s_", "")
    # remove the letters used in GTDB formating
    df_amp["phylum"] = df_amp["phylum"].str.replace(r"\s[A-Z](?!\w)", "", regex=True)
    df_amp["class"] = df_amp["class"].str.replace(r"\s[A-Z](?!\w)", "", regex=True)
    df_amp["order"] = df_amp["order"].str.replace(r"\s[A-Z](?!\w)", "", regex=True)
    df_amp["family"] = df_amp["family"].str.replace(r"\s[A-Z](?!\w)", "", regex=True)
    df_amp["genus"] = df_amp["genus"].str.replace(r"\s[A-Z](?!\w)", "", regex=True)
    df_amp["specie"] = df_amp["specie"].str.replace(r"\s[A-Z](?!\w)", "", regex=True)
    # remove the genus from specie column
    df_amp["specie_mod"] = df_amp["specie"].str.split(" ", n=1).str[1]
    
    ########################
    # (1-5) Kingdom//Phylum//Class/Genus
    ########################
    def create_taxonomy_nodes(df, level1, level2):
        """
        Create a dataframe of taxonomy nodes for the given levels:
        Kingdom/Phylum/Class/Order/Family/Genus/Specie.
        Parameters/inputs required:
            df (pandas.DataFrame): the input dataframe containing the taxonomy data.
            level1 (str): the name of the first level column.
            level2 (str): the name of the second level column.
        """
        df_tax = pd.DataFrame()
        df_tax[level1] = df[level1]
        df_tax[level2] = df[level2]
        df_tax = df_tax.groupby([level1, level2], sort=False, dropna=False).size().reset_index(name="count")
        df_tax[f"{level1}_id"] = pd.factorize(df_tax[level1])[0]
        max_value = (df_tax[f"{level1}_id"].max()+1)
        df_tax[f"{level2}_id"] = pd.factorize(df_tax[level2])[0] + max_value
        df_id = pd.melt(df_tax, value_vars=[f"{level1}_id", f"{level2}_id"], var_name="Category", value_name="node_id")
        df_name = pd.melt(df_tax, value_vars=[level1, level2], var_name="Category", value_name="label")
        df_tax_nodes = pd.concat([df_name, df_id["node_id"]], axis=1)
        df_tax_nodes.drop_duplicates(keep="first", inplace=True, ignore_index=True)
        return df_tax, df_tax_nodes, max_value
    df_amp_KP, df_amp_nodes_KP, max_value = create_taxonomy_nodes(df_amp, "kingdom", "phylum")
    df_amp_PC, df_amp_nodes_PC, max_value = create_taxonomy_nodes(df_amp, "phylum", "class")
    df_amp_CO, df_amp_nodes_CO, max_value = create_taxonomy_nodes(df_amp, "class", "order")
    df_amp_OF, df_amp_nodes_OF, max_value = create_taxonomy_nodes(df_amp, "order", "family")
    df_amp_FG, df_amp_nodes_FG, max_value = create_taxonomy_nodes(df_amp, "family", "genus")
    
    ########################
    # (6) Genus // Specie (sp.)
    ########################
    df_amp_GS = pd.DataFrame()
    df_amp_GS["genus"] = df_amp["genus"]
    df_amp_GS["specie"] = df_amp["specie_mod"]
    # count the number of times the combinations are there for specie+genus
    df_amp_GS = df_amp_GS.groupby(["genus", "specie"], sort=False, dropna=False).size().reset_index(name="count")
    # replace string values with unique numbers in new columns
    df_amp_GS["genus_id"] = pd.factorize(df_amp_GS["genus"])[0] + max_value
    max_value = (df_amp_GS["genus_id"].max()+1) # grab the maximum value from the column
    df_amp_GS["specie_id"] = pd.factorize(df_amp_GS["specie"])[0] + max_value
    # stack them vertically
    df_id = pd.melt(df_amp_GS, value_vars=["genus_id", "specie_id"], var_name="Category", value_name="node_id")
    df_name = pd.melt(df_amp_GS, value_vars=["genus", "specie"], var_name="Category", value_name="label")
    # merge the two melted DataFrames based on the index
    df_amp_nodes_GS = pd.concat([df_name, df_id["node_id"]], axis=1)
    # drop duplicates
    df_amp_nodes_GS.drop_duplicates(keep="first", inplace=True, ignore_index=True)
    
    ########################
    # (7) NODES labels
    ########################
    df_amp_nodes = pd.DataFrame()
    # concatenate all nodes" labels
    df_amp_nodes = pd.concat([df_amp_nodes_KP, df_amp_nodes_PC,
                              df_amp_nodes_CO,df_amp_nodes_OF,
                              df_amp_nodes_FG,df_amp_nodes_GS])
    # drop unnecessary columns
    df_amp_nodes.drop_duplicates(keep="first", inplace=True, ignore_index=True)
    values_to_remove = [ "Category", "node_id"] 
    df_amp_nodes.drop(values_to_remove,axis=1, inplace=True)
    # remove empty rows
    df_amp_nodes = df_amp_nodes.dropna()
    # assign a number from 0 to inf
    df_amp_nodes["node_id"] = range(len(df_amp_nodes))
    # replace data[0]["node"]["label"] / ["color"] with user input
    # convert column to list 
    column_list = df_amp_nodes["label"].tolist()
    # replace the "label" item in the "node" dictionary with the column list
    data[0]["node"]["label"] = column_list
    # generate distinct colors according to node_no
    nodes_no = len(column_list) #number of nodes
    color_list = []
    for i in range(nodes_no):
        hue = i / nodes_no
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        rgba = tuple(int(255 * x) for x in rgb) + (0.8,)
        color_string = f"rgba{rgba}"
        color_list.append(color_string)
    # replace the "color" item in the "node" dictionary with the color list
    # color_list =  ["blue"] * 137
    data[0]["node"]["color"] = color_list
    
    ########################
    # (8) COUNTS labels
    ########################
    # replace the contents of xx_id with the correct digits
    # drop unnecessary columns
    dataframes = [df_amp_KP, df_amp_PC, df_amp_CO, df_amp_OF, df_amp_FG, df_amp_GS]
    for df in dataframes:
        columns_to_remove = [col for col in df.columns if "_id" in col]
        df.drop(columns_to_remove, axis=1, inplace=True)
    # stack columns in order
    # rename columns
    dataframes = [df_amp_KP, df_amp_PC, df_amp_CO, df_amp_OF, df_amp_FG, df_amp_GS]
    for df in dataframes:
        df.columns = ["source", "target", "count"]
    df_amp_counts = pd.concat([df_amp_KP, df_amp_PC, df_amp_CO,
                               df_amp_OF, df_amp_FG, df_amp_GS], axis=0, ignore_index=True)
    # remove rows that have no values in two columns
    df_amp_counts = df_amp_counts.dropna(subset=["source", "target"])
    # labels and digits to dict
    label_dict = df_amp_nodes.set_index("label")["node_id"].to_dict()
    # replace the values in the "source" column with digits
    df_amp_counts["source_digit"] = df_amp_counts["source"].replace(label_dict).astype(int)
    # replace the values in the "target" column with digits
    #df_amp_counts["target_digit"] = df_amp_counts["target"].replace(label_dict)
    df_amp_counts["target_digit"] = df_amp_counts["target"].map(label_dict).astype(int)
    # replace data[0]["link"]["source"] / ["target"] / ["value"] / ["color"] with user input
    # convert columns to list 
    column_list = df_amp_counts["count"].tolist()
    data[0]["link"]["value"] = column_list
    column_list = df_amp_counts["target_digit"].tolist()
    data[0]["link"]["target"] = column_list
    column_list = df_amp_counts["source_digit"].tolist()
    data[0]["link"]["source"] = column_list
    # make sure the values in the list are integers 
    data[0]["link"]["source"] = [int(src) for src in data[0]["link"]["source"]]
    data[0]["link"]["target"] = [int(src) for src in data[0]["link"]["target"]]
    data[0]["link"]["value"] = [int(src) for src in data[0]["link"]["value"]]
    
    ########################
    # (9) Prepare for the Sankey diagram
    ########################
    # Adapted from https://python-graph-gallery.com/sankey-diagram-with-python-and-plotly/
    # override gray link colors with "source" colors
    opacity = 0.4
    # change "magenta" to its "rgba" value to add opacity
    data[0]["node"]["color"] = ["rgba(255,0,255, 0.8)" if color == "magenta" else color for color in data[0]["node"]["color"]]
    data[0]["link"]["color"] = [data[0]["node"]["color"][src].replace("0.8", str(opacity))
                                        for src in data[0]["link"]["source"]]
    # change opacity of the links
    data[0]["link"]["color"] = [color.replace("0.4", "0.2") for color in data[0]["link"]["color"]]
    
    fig = go.Figure(data=[go.Sankey(
        valueformat = ".0f",
        valuesuffix = "TWh",
        # Define nodes
        node = dict(
          pad = 15,
          thickness = 15,
          line = dict(color = "black", width = 0.5),
          label =  data[0]["node"]["label"],
          color =  data[0]["node"]["color"],
          hovertemplate="%{label}<extra></extra>",
          hoverlabel=dict(font=dict(family="Arial")),
          ),
        # Add links
        link = dict(
          source =  data[0]["link"]["source"],
          target =  data[0]["link"]["target"],
          value =  data[0]["link"]["value"],
          label =  data[0]["link"]["value"],
          color =  data[0]["link"]["color"]
    ))],)             
    fig.update_layout(title_text="Contig taxonomic lineage for AMP hits based on MMseqs2 classification - Sankey plot ",
                      font_size=12)
    #show plot:
    #fig.show()

    fig.update_layout(
        font=dict(family="Arial", size=10.5, color="black"),
        hoverlabel=dict(font=dict(family="Arial"))
    )
    #save the plot in html format :
    #fig.write_html("combgc_sankey_plot.html")
    #fig.write_image("combgc_sankey_plot.pdf")
    #fig.write_image("combgc_sankey_plot.png", scale=5)
    return fig.show()
