import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

def create_grid_chart(row_groups, group_sizes, text_data=None, window_size=(800, 600)):
    """
    Create a scrollable grid chart with 7 columns and variable row groups, displaying text data
    with column widths scaled to fit text content.
    
    Parameters:
    row_groups (int): Number of row groups
    group_sizes (list): List of integers (2 or 3) specifying sub-rows per group
    text_data (list): 2D list of strings for cell content (optional)
    window_size (tuple): Window size as (width, height) in pixels
    """
    # Validate inputs
    if len(group_sizes) != row_groups:
        raise ValueError("group_sizes length must match row_groups")
    if not all(size in [1, 2, 3] for size in group_sizes):
        raise ValueError("group_sizes must contain only 2 or 3")
    
    # Calculate total rows
    total_rows = sum(group_sizes)
    columns = 8
    
    # Create default text data if none provided
    if text_data is None:
        text_data = [[f'Data {i+1},{j+1}' for j in range(columns)] for i in range(total_rows)]
    else:
        # Validate text_data dimensions
        if len(text_data) != total_rows or any(len(row) != columns for row in text_data):
            raise ValueError(f"text_data must be {total_rows}x{columns}")
    
    # Create Tkinter window
    root = tk.Tk()
    root.title("Scrollable Grid Chart")
    
    # Create scrollable frame
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack widgets tightly
    canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
    scrollbar.pack(side="right", fill="y", padx=0, pady=0)
    main_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create matplotlib figure
    # Base figure width adjusted dynamically later
    fig, ax = plt.subplots(figsize=(10, 30))
    
    # Calculate maximum text length per column for scaling
    col_widths = [1] * columns
    for j in range(columns):
        for i in range(total_rows):
            text = str(text_data[i][j])
            # Estimate text width (approximate, depends on font)
            text_width = math.ceil(len(text) * .2)
            col_widths[j] = max(col_widths[j], text_width)
    
    # Adjust figure width based on total text content
    fig.set_size_inches(max(8, sum(col_widths) * .625), max(2, total_rows * 0.6))
    
    # Create empty grid for background
    grid_data = np.zeros((total_rows, columns))
    cax = ax.matshow(grid_data, cmap='Greys', alpha=0.2)

    # Add text to each cell
    for i in range(total_rows):
        for j in range(columns):
            # Adjust text x-position to center within scaled column
            x_pos = sum(col_widths[:j]) + (col_widths[j] - 1) / 2
            ax.text(x_pos, i, text_data[i][j], ha='center', va='center', fontsize=10) # 
    
    # Set grid lines with custom column positions
    ax.set_xticks(np.cumsum([0] + col_widths[:-1]) - 0.5)
    ax.set_yticks(np.arange(-0.5, total_rows, 1))
    ax.grid(True, color='black', linewidth=1)
    
    # Customize y-axis labels to show group structure
    y_labels = []
    row_counter = 0
    for group_idx, size in enumerate(group_sizes):
        for sub_row in range(size):
            y_labels.append(f'Group {group_idx + 1}.{sub_row + 1}')
            row_counter += 1
    ax.set_yticklabels([''] + y_labels)

    # Set x-axis labels for headers at column centers
    x_label_positions = [sum(col_widths[:j]) + (col_widths[j] - 1) / 2 for j in range(columns)]
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_locator(ticker.FixedLocator(x_label_positions))
    ax.set_xticklabels(["Intersection", "Tile", "Number", "RP", "DCP", "Settle", "City", "RP"], minor=True, ha='center')
   
    # Move header labels to column centers without affecting grid ticks
    for tick, x_pos in zip(ax.get_xticklabels(), x_label_positions):
        tick.set_x(x_pos)
    
    # Add group separators
    row_counter = 0
    for size in group_sizes[:-1]:  # Exclude last group
        row_counter += size
        ax.axhline(row_counter - 0.5, color='red', linestyle='--', linewidth=2)
    
    # Customize appearance
    ax.tick_params(axis='y', which='both', length=0)
    ax.tick_params(axis='x', which='both', length=0)
    ax.set_title('Grid Chart with Text Data')
    
    # Set x-axis limits to match scaled columns
    ax.set_xlim(-0.5, sum(col_widths) - 0.5)
    
    # Minimize whitespace in figure
#    fig.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)
    plt.tight_layout(pad=0.5)

    # Embed matplotlib figure in Tkinter
    canvas_agg = FigureCanvasTkAgg(fig, master=scrollable_frame)
    canvas_agg.draw()
    canvas_agg.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

    # Adjust window size
    root.geometry(f"{window_size[0]}x{window_size[1]}")
    
    # Handle window close event to prevent hanging
    def on_closing():
        plt.close(fig)  # Close matplotlib figure
        root.quit()     # Stop Tkinter mainloop
        root.destroy()  # Destroy Tkinter window
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start Tkinter main loop
    root.mainloop()

# Example usage
if __name__ == "__main__":
    # Example: 5 groups with varying sub-rows and varied text lengths
    example_text_data = [
        ['Short', 'Medium Text', 'Very Long Text Here', 'A', 'B', 'C', 'D', 'F'],
        ['A2', 'Longer Text', 'Short', 'E', 'F', 'G', 'H', 'F'],
        ['A3', 'B3', 'C3', 'Very Long Entry', 'E3', 'F3', 'G3', 'F'],
        ['A4', 'B4', 'C4', 'D4', 'Extra Long Text', 'F4', 'G4', 'F'],
        ['A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'Very Long', 'F'],
        ['A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'F'],
        ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'F'],
        ['A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'Very Long Text', 'F'],
        ['A9', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'F'],
        ['A10', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'F'],
        ['A11', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11', 'F'],
        ['A12', 'B12', 'C12', 'D12', 'E12', 'F12', 'Extra Long', 'F']
    ]
    create_grid_chart(row_groups=6, group_sizes=[1, 1, 3, 2, 3, 2], text_data=example_text_data)