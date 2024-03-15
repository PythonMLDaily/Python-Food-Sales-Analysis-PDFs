import pandas as pd
from datetime import time
from itertools import combinations
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import gridspec

file_path_square = './data/items-2023-11-01-2023-12-01.csv'
file_path_toast = './data/ItemSelectionDetails_2023_11_14-2023_12_13.csv'
square_df = pd.read_csv(file_path_square)
toast_df = pd.read_csv(file_path_toast, encoding='ISO-8859-1')

output_information = {}


def set_square_service_times(df, times):
    # Function to determine the service based on a given time
    def determine_service(record_time):
        for service, (start, end) in times.items():
            if start <= record_time < end:
                return service
        return "Undefined"

    # Convert 'Time' column to Python time objects for comparison
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time

    # Apply the service categorization
    df['Service'] = df['Time'].apply(determine_service)

    return df


# ======================================

# # **Task 2 - Convert Data to Standard Format**
# Now, we'll proceed with converting both Toast POS and Square POS data
# to the standard Flapjack format.
# This format includes the following columns: date, item, price, and order_id.

# Converting Toast POS Data to Standard Format

toast_df['Net Price'] = toast_df['Net Price'].replace('[\\$,]', '', regex=True).astype(float)
toast_columns_mapping = {
    'Order Date': 'date',
    'Menu Item': 'item',
    'Net Price': 'price',
    'Order Id': 'order_id'
}
toast_standard_df = toast_df[toast_columns_mapping.keys()].rename(columns=toast_columns_mapping)

toast_standard_df['order_id'] = toast_standard_df['order_id'].astype(str)  # Convert price from string to float and order_id to string
square_df['Gross Sales'] = square_df['Gross Sales'].replace('[\\$,]', '', regex=True).astype(float)  # Converting Square POS Data to Standard Format

service_times = {
    'Breakfast': (time(8, 0), time(12, 0)),
    'Dinner': (time(12, 0), time(23, 59))
}
square_df_service_categorized = set_square_service_times(square_df.copy(), service_times)

# Selecting and renaming the relevant columns for Square data
square_columns_mapping = {
    'Date': 'date',
    'Item': 'item',
    'Gross Sales': 'price',
    'Service': 'order_id'  # Using the 'Service' column as a placeholder for 'order_id'
}
square_standard_df = square_df_service_categorized[square_columns_mapping.keys()].rename(columns=square_columns_mapping)

output_information['task_2'] = {
    'square_df_service_categorized': square_df_service_categorized,
    'square_standard_df': square_standard_df
}

# ======================================

# # **Task 3 - Top Selling Times/Services**
# In this task, we will analyze the sales data to uncover insights into:
#
# Gross Sales Throughout the Day (Grouped by Hour): Identifying peak sales times.
# Revenue by Service: Determining which service generates the most sales.
# Revenue Throughout the Week: Analyzing which day of the week records the most sales.


# Converting 'date' columns to datetime for both datasets
toast_standard_df['date'] = pd.to_datetime(toast_standard_df['date'], format='mixed')
square_standard_df['date'] = pd.to_datetime(square_standard_df['date'])

# Extracting hour from the datetime for analysis
toast_standard_df['hour'] = toast_standard_df['date'].dt.hour
square_standard_df['hour'] = square_standard_df['date'].dt.hour

# Grouping by hour and summing up the sales for Toast data
toast_sales_by_hour = toast_standard_df.groupby('hour')['price'].sum()

# Grouping by hour and summing up the sales for Square data
square_sales_by_hour = square_standard_df.groupby('hour')['price'].sum()

# Grouping Toast data by service and summing up the sales
toast_sales_by_service = toast_standard_df.groupby(toast_df['Service'])['price'].sum()

# Extracting day of the week from the datetime (0=Monday, 6=Sunday)
toast_standard_df['day_of_week'] = toast_standard_df['date'].dt.dayofweek
square_standard_df['day_of_week'] = square_standard_df['date'].dt.dayofweek

# Grouping by day of the week and summing up the sales for Toast data
toast_sales_by_day_of_week = toast_standard_df.groupby('day_of_week')['price'].sum()

# Grouping by day of the week and summing up the sales for Square data
square_sales_by_day_of_week = square_standard_df.groupby('day_of_week')['price'].sum()

output_information['task_3'] = {
    'toast_sales_by_hour': toast_sales_by_hour,
    'square_sales_by_hour': square_sales_by_hour,
    'toast_sales_by_service': toast_sales_by_service,
    'toast_sales_by_day_of_week': toast_sales_by_day_of_week,
    'square_sales_by_day_of_week': square_sales_by_day_of_week
}

# =====================================

# # **Task 4 - Top Selling Categories**
# In this task, we'll focus on analyzing the top-selling categories by:
#
# Ranking Categories by Sales Volume: Identifying which categories generate the most sales.
# Calculating Average Sale Price per Category: Finding the average price for items in each category.
# Determining the Percentage of Total Sales per Category:
# Assessing how much each category contributes to the overall sales.
# Focusing on Dine-In Sales Data Only: We'll filter out non-dine-in sales.


# Filtering Square data for Dine-In sales only
square_dine_in_df = square_df[square_df['Dining Option'] == 'For Here']

# Grouping by category for sales volume and average sale price
category_sales_volume = square_dine_in_df.groupby('Item')['Gross Sales'].sum().sort_values(ascending=False)
category_average_price = square_dine_in_df.groupby('Item')['Gross Sales'].mean()
square_dine_in_df.groupby('Item')['Gross Sales'].sum().sort_values(ascending=False).head().plot()

# Calculating the percentage of total sales per category
total_sales = square_dine_in_df['Gross Sales'].sum()
category_sales_percentage = (category_sales_volume / total_sales) * 100

category_analysis_square = pd.DataFrame({
    'Sales Volume': category_sales_volume,
    'Average Price': category_average_price,
    'Percentage of Total Sales': category_sales_percentage
})

# Filtering Toast data for Dine-In sales only
toast_dine_in_df = toast_df[toast_df['Dining Option'] == 'Dine In']

# Grouping by menu item for sales volume and average sale price
menu_item_sales_volume = toast_dine_in_df.groupby('Menu Item')['Net Price'].sum().sort_values(ascending=False)
menu_item_average_price = toast_dine_in_df.groupby('Menu Item')['Net Price'].mean()

# Calculating the percentage of total sales per menu item
total_sales_toast = toast_dine_in_df['Net Price'].sum()
menu_item_sales_percentage = (menu_item_sales_volume / total_sales_toast) * 100

menu_item_analysis_toast = pd.DataFrame({
    'Sales Volume': menu_item_sales_volume,
    'Average Price': menu_item_average_price,
    'Percentage of Total Sales': menu_item_sales_percentage
})

output_information['task_4'] = {
    'category_analysis_square': category_analysis_square,
    'menu_item_analysis_toast': menu_item_analysis_toast
}

# ==================================

# # **Task 5 - Top Selling Categories by Service**
# In this task, we'll analyze the top-selling categories grouped by service.


# Grouping Toast data by service and menu item for sales volume and average sale price
service_category_sales_volume = toast_dine_in_df.groupby(['Service', 'Menu Item'])['Net Price'].sum().sort_values(ascending=False)
service_category_average_price = toast_dine_in_df.groupby(['Service', 'Menu Item'])['Net Price'].mean()

# Calculating the percentage of total sales per category within each service
service_total_sales = toast_dine_in_df.groupby('Service')['Net Price'].sum()
service_category_sales_percentage = service_category_sales_volume.div(service_total_sales, level='Service') * 100

service_category_analysis_toast = pd.DataFrame({
    'Sales Volume': service_category_sales_volume,
    'Average Price': service_category_average_price,
    'Percentage of Total Sales': service_category_sales_percentage
}).reset_index()

output_information['task_5'] = {
    'service_category_analysis_toast': service_category_analysis_toast
}

# ==========================================

# # **Task 6 - Top Selling Dishes**
# For this task, we will identify top 10 selling dishes by gross sales per category, focusing on dine-in sales only.
# We'll calculate:
#
# The Gross Sales per Dish.
# The Percentage of Total Sales Each Dish Represents.
# The Percentage of Category Sales Each Dish Represents.

# Filtering for dine-in sales only
square_dine_in_df = square_df[square_df['Dining Option'] == 'For Here']

# Grouping by category and item for sales volume
dish_sales_volume_square = square_dine_in_df.groupby(['Category', 'Item'])['Gross Sales'].sum().sort_values(ascending=False)

# Calculating the percentage of total sales and category sales each dish represents
total_sales_square = square_dine_in_df['Gross Sales'].sum()
category_sales_square = square_dine_in_df.groupby('Category')['Gross Sales'].sum()
dish_total_sales_percentage_square = (dish_sales_volume_square / total_sales_square) * 100
dish_category_sales_percentage_square = dish_sales_volume_square.div(category_sales_square, level='Category') * 100

# Combining the data into a single DataFrame
top_dishes_square = pd.DataFrame({
    'Gross Sales': dish_sales_volume_square,
    'Percentage of Total Sales': dish_total_sales_percentage_square,
    'Percentage of Category Sales': dish_category_sales_percentage_square
})

# Grouping by menu item for sales volume (without category) for Toast data
dish_sales_volume_toast = toast_dine_in_df.groupby('Menu Item')['Net Price'].sum().sort_values(ascending=False)

# Calculating the percentage of total sales each dish represents
dish_total_sales_percentage_toast = (dish_sales_volume_toast / total_sales_toast) * 100

# Combining the data into a single DataFrame
top_dishes_toast_no_category = pd.DataFrame({
    'Gross Sales': dish_sales_volume_toast,
    'Percentage of Total Sales': dish_total_sales_percentage_toast
})

output_information['task_6'] = {
    'top_dishes_square': top_dishes_square,
    'top_dishes_toast_no_category': top_dishes_toast_no_category
}

# ==========================================

# # **Task 7 - Top Selling Dishes by Service**
# Next, we'll group data by service and rank top 10 dishes by greatest sales volume, again focusing on dine-in only.

# Grouping Toast data by service and menu item for sales volume
service_dish_sales_volume_toast = toast_dine_in_df.groupby(['Service', 'Menu Item'])['Net Price'].sum().sort_values(ascending=False)

# Calculating the percentage of total sales and service sales each dish represents
service_total_sales_toast = toast_dine_in_df.groupby('Service')['Net Price'].sum()
service_dish_total_sales_percentage_toast = service_dish_sales_volume_toast.div(service_total_sales_toast, level='Service') * 100

# Combining the data into a single DataFrame
top_dishes_by_service_toast = pd.DataFrame({
    'Gross Sales': service_dish_sales_volume_toast,
    'Percentage of Total Sales': service_dish_total_sales_percentage_toast
})

output_information['task_7'] = {
    'top_dishes_by_service_toast': top_dishes_by_service_toast
}

# ==========================================

# # **Task 8 - Items Commonly Sold Together**
# This task involves identifying the top 20 pairs of items that are most commonly sold together.

# Grouping items by Transaction ID to find combinations
grouped_items = square_dine_in_df.groupby('Transaction ID')['Item'].apply(list)

# Generate all item pairs within each transaction, excluding duplicates and self-pairs
item_pairs = Counter()
for items in grouped_items:
    for item_pair in combinations(set(items), 2):
        # Sorting the pair to treat different orderings as the same (e.g., A-B and B-A)
        item_pairs[tuple(sorted(item_pair))] += 1

# Get the top 20 most common pairs
top_20_pairs = item_pairs.most_common(20)

# Convert to DataFrame for further analysis
top_20_pairs_df = pd.DataFrame(top_20_pairs, columns=['Item Pair', 'Frequency'])

# Calculate additional metrics
top_20_pairs_df['Probability of Pair Sold Together'] = top_20_pairs_df['Frequency'] / len(grouped_items)
top_20_pairs_df['Total Sales Volume'] = top_20_pairs_df['Item Pair'].apply(
    lambda x: square_dine_in_df[
        square_dine_in_df['Item'].isin(x)
    ]['Gross Sales'].sum()
)

# Filter out non-dine-in sales
toast_dine_in_df = toast_df[toast_df['Dining Option'] == 'Dine In']

# Grouping items by Order Id to find combinations
grouped_items_toast = toast_dine_in_df.groupby('Order Id')['Menu Item'].apply(list)

# Generate all item pairs within each order, excluding duplicates and self-pairs
item_pairs_toast = Counter()
for items in grouped_items_toast:
    for item_pair in combinations(set(items), 2):
        # Sorting the pair to treat different orderings as the same
        item_pairs_toast[tuple(sorted(item_pair))] += 1

# Get the top 20 most common pairs for Toast data
top_20_pairs_toast = item_pairs_toast.most_common(20)

# Convert to DataFrame for further analysis
top_20_pairs_toast_df = pd.DataFrame(top_20_pairs_toast, columns=['Item Pair', 'Frequency'])

# Calculate additional metrics for Toast data
top_20_pairs_toast_df['Probability of Pair Sold Together'] = top_20_pairs_toast_df['Frequency'] / len(grouped_items_toast)
top_20_pairs_toast_df['Total Sales Volume'] = top_20_pairs_toast_df['Item Pair'].apply(
    lambda x: toast_dine_in_df[
        toast_dine_in_df['Menu Item'].isin(x)
    ]['Net Price'].sum()
)

output_information['task_8'] = {
    'top_20_pairs_df': top_20_pairs_df,
    'top_20_pairs_toast_df': top_20_pairs_toast_df
}

# ==========================================

# # **Task 9 - Categories Commonly Sold Together**
# This task involves identifying categories that are commonly sold together.


# Grouping items by Transaction ID to find category combinations
grouped_categories = square_dine_in_df.groupby('Transaction ID')['Category'].apply(list)

# Generate all category pairs within each transaction, excluding duplicates and self-pairs
category_pairs = Counter()
for categories in grouped_categories:
    for category_pair in combinations(set(categories), 2):
        # Sorting the pair to treat different orderings as the same
        category_pair = {str(category_pair[0]), str(category_pair[1])}
        category_pairs[tuple(sorted(category_pair))] += 1

# Get the top 20 most common category pairs
top_category_pairs = category_pairs.most_common(20)

# Convert to DataFrame for further analysis
top_category_pairs_df = pd.DataFrame(top_category_pairs, columns=['Category Pair', 'Frequency'])

# Calculate additional metrics
top_category_pairs_df['Probability of Category Pair Sold Together'] = top_category_pairs_df['Frequency'] / len(grouped_categories)
top_category_pairs_df['Total Sales Volume'] = top_category_pairs_df['Category Pair'].apply(
    lambda x: square_dine_in_df[
        square_dine_in_df['Category'].isin(x)
    ]['Gross Sales'].sum()
)

# Handling null or problematic values in 'Menu Group'
toast_dine_in_df.loc[:, 'Menu Group'] = toast_dine_in_df['Menu Group'].fillna('Unknown').astype(str)
grouped_menu_groups = toast_dine_in_df.groupby('Order Id')['Menu Group'].apply(list)

# Regenerate Menu Group pairs with the corrected data
menu_group_pairs_corrected = Counter()
for menu_groups in grouped_menu_groups:
    # Ensure all menu groups are strings and filter out any 'Unknown' or empty groups
    cleaned_menu_groups = [str(group) for group in menu_groups if group and group != 'Unknown']
    for menu_group_pair in combinations(set(cleaned_menu_groups), 2):
        menu_group_pairs_corrected[tuple(sorted(menu_group_pair))] += 1

# Get the top 20 most common Menu Group pairs with corrected data
top_menu_group_pairs_corrected = menu_group_pairs_corrected.most_common(20)

# Convert to DataFrame for further analysis
top_menu_group_pairs_corrected_df = pd.DataFrame(top_menu_group_pairs_corrected, columns=['Menu Group Pair', 'Frequency'])

# Calculate additional metrics for corrected data
top_menu_group_pairs_corrected_df['Probability of Menu Group Pair Sold Together'] = top_menu_group_pairs_corrected_df['Frequency'] / len(grouped_menu_groups)
top_menu_group_pairs_corrected_df['Total Sales Volume'] = top_menu_group_pairs_corrected_df['Menu Group Pair'].apply(
    lambda x: toast_dine_in_df[
        toast_dine_in_df['Menu Group'].isin(x)
    ]['Net Price'].sum()
)

output_information['task_9'] = {
    'top_category_pairs_df': top_category_pairs_df,
    'top_menu_group_pairs_corrected_df': top_menu_group_pairs_corrected_df
}


# ==========================================

# Export everything to a PDF file

def add_chart_plot(df, title, kind, x, y, show_legend=False, bottom_adjustment: float | None = 0.5, left_adjustment=None):
    df.plot(
        title=title,
        kind=kind,
        x=x,
        y=y,
        legend=show_legend
    )
    plt.subplots_adjust(bottom=bottom_adjustment, left=left_adjustment)
    pdf.savefig()
    plt.close()


with PdfPages('pdfoutput.pdf') as pdf:
    # Sets the grid for the plots to be max size
    gs = gridspec.GridSpec(29, 21, wspace=0.1, hspace=0.1)
    # Sets the font size for the plots
    plt.rcParams.update({'font.size': 8})

    # Customization options:
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html
    # https://pandas.pydata.org/docs/reference/api/pandas.plotting.table.html
    # top_menu_group_pairs_corrected_df.plot(
    #     title="Top Menu Group Pairs Sold Together",
    #     table=True
    # )

    # Missing tasks and reasons:
    # - 1 -> Not in our file
    # - 2 -> Conversion to standard formats

    # Task 3:
    add_chart_plot(
        df=output_information['task_3']['toast_sales_by_hour'],
        title="#3-Sales by hour",
        kind='bar',
        x='hour',
        y=None,
        bottom_adjustment=None
    )
    add_chart_plot(
        df=output_information['task_3']['toast_sales_by_service'].head(30),
        title="#3-Sales by service",
        kind='barh',
        x='Service',
        y=None,
        bottom_adjustment=None,
        left_adjustment=0.2
    )
    add_chart_plot(
        df=output_information['task_3']['toast_sales_by_day_of_week'].head(30),
        title="#3-Sales by Day of Week",
        kind='barh',
        x='day_of_week',
        y=None,
        bottom_adjustment=None,
        left_adjustment=0.2
    )
    # End of Task 3

    # Task 4:
    category_analysis_square = output_information['task_4']['category_analysis_square'].map(lambda x: round(x, 2))
    add_chart_plot(
        df=category_analysis_square.sort_values("Sales Volume", ascending=False).head(30),
        title="#4-Item Sales Volume",
        kind='bar',
        x=None,
        y='Sales Volume'
    )
    add_chart_plot(
        df=category_analysis_square.sort_values('Average Price', ascending=False).head(30),
        title="#4-Average Price",
        kind='bar',
        x=None,
        y='Average Price'
    )
    add_chart_plot(
        df=category_analysis_square.sort_values('Percentage of Total Sales', ascending=False).head(30),
        title="#4-Percentage of Total Sales",
        kind='bar',
        x=None,
        y='Percentage of Total Sales'
    )
    add_chart_plot(
        df=output_information['task_4']['menu_item_analysis_toast'].sort_values("Sales Volume", ascending=False).head(30),
        title="#4-Menu Item Sales Volume",
        kind='bar',
        x=None,
        y='Sales Volume'
    )
    add_chart_plot(
        df=output_information['task_4']['menu_item_analysis_toast'].sort_values('Average Price', ascending=False).head(30),
        title="#4-Menu Item Average Price",
        kind='bar',
        x=None,
        y='Average Price'
    )
    add_chart_plot(
        df=output_information['task_4']['menu_item_analysis_toast'].sort_values('Percentage of Total Sales', ascending=False).head(30),
        title="#4-Percentage of Total Sales",
        kind='bar',
        x=None,
        y='Percentage of Total Sales'
    )
    # End of Task 4

    # Task 5:
    for service_time in output_information['task_5']['service_category_analysis_toast']['Service'].unique():
        add_chart_plot(
            df=output_information['task_5']['service_category_analysis_toast'].query("`Service` == @service_time").sort_values('Sales Volume', ascending=False).head(30),
            title=f"#5-Sales Volume in {service_time} service",
            kind='barh',
            x='Menu Item',
            y='Sales Volume',
            bottom_adjustment=None,
            left_adjustment=0.5
        )
        add_chart_plot(
            df=output_information['task_5']['service_category_analysis_toast'].query("`Service` == @service_time").sort_values('Average Price', ascending=False).head(30),
            title=f"#5-Average Price in {service_time} service",
            kind='barh',
            x='Menu Item',
            y='Average Price',
            bottom_adjustment=None,
            left_adjustment=0.5
        )
        add_chart_plot(
            df=output_information['task_5']['service_category_analysis_toast'].query("`Service` == @service_time").sort_values('Percentage of Total Sales', ascending=False).head(30),
            title=f"#5-Percentage of total sales in {service_time} service",
            kind='barh',
            x='Menu Item',
            y='Percentage of Total Sales',
            bottom_adjustment=None,
            left_adjustment=0.5
        )
        for service_time in output_information['task_5']['service_category_analysis_toast']['Service'].unique():
            add_chart_plot(
                df=output_information['task_5']['service_category_analysis_toast'].query("`Service` == @service_time").sort_values('Percentage of Total Sales', ascending=False).head(30),
                title=f"#5-Percentage of item sale in {service_time} service",
                kind='bar',
                x='Menu Item',
                y='Percentage of Total Sales'
            )
    # End of Task 5

    # Task 6:
    add_chart_plot(
        df=output_information['task_6']['top_dishes_toast_no_category'].sort_values('Gross Sales', ascending=False).head(30),
        title="#6-Top Dishes Sold",
        kind='barh',
        x=None,
        y='Gross Sales',
        bottom_adjustment=0.1,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_6']['top_dishes_toast_no_category'].sort_values('Percentage of Total Sales', ascending=False).head(30),
        title="#6-Top Dishes Sold by Percentage",
        kind='barh',
        x=None,
        y='Percentage of Total Sales',
        bottom_adjustment=0.1,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_6']['top_dishes_square'].sort_values('Gross Sales', ascending=False).head(30),
        title="#6-Top Dishes (with category) Sold",
        kind='barh',
        x=None,
        y='Gross Sales',
        bottom_adjustment=0.1,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_6']['top_dishes_square'].sort_values('Percentage of Category Sales', ascending=False).head(30),
        title="#6-Top Dishes (with category) Sold by Percentage",
        kind='barh',
        x=None,
        y='Percentage of Category Sales',
        bottom_adjustment=0.1,
        left_adjustment=0.5
    )
    # End of Task 6

    # Task 7:
    # Note: @povilas -> Possible content about grouped index search
    for service_time in output_information['task_7']['top_dishes_by_service_toast'].index.get_level_values(0).unique():
        add_chart_plot(
            # Note: @povilas -> Possible content about grouped index search
            df=output_information['task_7']['top_dishes_by_service_toast'].query("index.to_series().str[0] == @service_time").sort_values('Gross Sales', ascending=False).head(30),
            title=f"#7-Gross Sales in {service_time} service",
            kind='barh',
            x=None,
            y='Gross Sales',
            bottom_adjustment=None,
            left_adjustment=0.5
        )
        add_chart_plot(
            df=output_information['task_7']['top_dishes_by_service_toast'].query("index.to_series().str[0] == @service_time").sort_values('Percentage of Total Sales', ascending=False).head(30),
            title=f"#7-Percentage of Total Sales in {service_time} service",
            kind='barh',
            x=None,
            y='Percentage of Total Sales',
            bottom_adjustment=None,
            left_adjustment=0.5
        )
    # End of Task 7

    # Task 8:
    add_chart_plot(
        df=output_information['task_8']['top_20_pairs_df'].sort_values('Frequency', ascending=False),
        title="#8-Top 20 pairs of items sold together - Frequency",
        kind='barh',
        x='Item Pair',
        y='Frequency',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_8']['top_20_pairs_df'].sort_values('Probability of Pair Sold Together', ascending=False),
        title="#8-Top 20 pairs of items sold together - Pair Sold Together",
        kind='barh',
        x='Item Pair',
        y='Probability of Pair Sold Together',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_8']['top_20_pairs_df'].sort_values('Total Sales Volume', ascending=False),
        title="#8-Top 20 pairs of items sold together - Total Sales Volume",
        kind='barh',
        x='Item Pair',
        y='Total Sales Volume',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_8']['top_20_pairs_toast_df'].sort_values('Frequency', ascending=False),
        title="#8-Top 20 pairs of items sold together - Frequency",
        kind='barh',
        x='Item Pair',
        y='Frequency',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_8']['top_20_pairs_toast_df'].sort_values('Probability of Pair Sold Together', ascending=False),
        title="#8-Top 20 pairs of items sold together - Probability of Pair Sold Together",
        kind='barh',
        x='Item Pair',
        y='Probability of Pair Sold Together',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_8']['top_20_pairs_toast_df'].sort_values('Total Sales Volume', ascending=False),
        title="#8-Top 20 pairs of items sold together - Total Sales Volume",
        kind='barh',
        x='Item Pair',
        y='Total Sales Volume',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    # End of Task 8

    # Task 9:
    add_chart_plot(
        df=output_information['task_9']['top_menu_group_pairs_corrected_df'].sort_values("Total Sales Volume", ascending=False),
        title="#9-Top Menu Group Pairs Sold Together",
        kind='bar',
        x='Menu Group Pair',
        y='Total Sales Volume'
    )
    add_chart_plot(
        df=output_information['task_9']['top_menu_group_pairs_corrected_df'].sort_values("Probability of Menu Group Pair Sold Together", ascending=False),
        title="#9-Probability of Menu Group Pair Sold Together",
        kind='bar',
        x='Menu Group Pair',
        y='Probability of Menu Group Pair Sold Together'
    )
    add_chart_plot(
        df=output_information['task_9']['top_menu_group_pairs_corrected_df'].sort_values("Frequency", ascending=False),
        title="#9-Frequency",
        kind='bar',
        x='Menu Group Pair',
        y='Frequency'
    )
    add_chart_plot(
        df=output_information['task_9']['top_menu_group_pairs_corrected_df'].sort_values('Frequency', ascending=False),
        title="#9-Top Menu Group Pairs - Frequency",
        kind='barh',
        x='Menu Group Pair',
        y='Frequency',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_9']['top_menu_group_pairs_corrected_df'].sort_values('Probability of Menu Group Pair Sold Together', ascending=False),
        title="#9-Top Menu Group Pairs - Menu Group Pair Sold Together",
        kind='barh',
        x='Menu Group Pair',
        y='Probability of Menu Group Pair Sold Together',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_9']['top_menu_group_pairs_corrected_df'].sort_values('Total Sales Volume', ascending=False),
        title="#9-Top Menu Group Pairs - Total Sales Volume",
        kind='barh',
        x='Menu Group Pair',
        y='Total Sales Volume',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_9']['top_category_pairs_df'].sort_values('Frequency', ascending=False),
        title="#9-Top 20 pairs of categories - Frequency",
        kind='barh',
        x='Category Pair',
        y='Frequency',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_9']['top_category_pairs_df'].sort_values('Probability of Category Pair Sold Together', ascending=False),
        title="#9-Top 20 pairs of categories - Category Pair Sold Together",
        kind='barh',
        x='Category Pair',
        y='Probability of Category Pair Sold Together',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    add_chart_plot(
        df=output_information['task_9']['top_category_pairs_df'].sort_values('Total Sales Volume', ascending=False),
        title="#9-Top 20 pairs of categories - Total Sales Volume",
        kind='barh',
        x='Category Pair',
        y='Total Sales Volume',
        bottom_adjustment=None,
        left_adjustment=0.5
    )
    # End of Task 9
