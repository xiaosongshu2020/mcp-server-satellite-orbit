import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

class colorEnumerator:
    """
    RGB Color Enumerator: Defines a series of RGB colors suitable for scientific papers.
    Each call returns the next color. Colors are enumerated in sequence,
    without repetition or disorder.
    """
    
    def __init__(self):
        # Define RGB color list suitable for scientific papers
        # These colors are carefully selected for good distinction and print quality
        self.colors = [
            [213, 39, 40],    # Red
            [204, 121, 167],  # Magenta
            [0, 158, 115],    # Teal
            [213, 94, 0],     # Orange
            [0, 114, 178],    # Blue
            [240, 228, 66],   # Yellow
            [0, 0, 0],        # Black
            [86, 180, 233],   # Sky Blue
            [230, 159, 0],    # Amber
            [0, 102, 0],      # Dark Green
            [132, 0, 198],    # Purple
            [100, 100, 100],  # Gray
            [158, 115, 0],    # Brown
            [70, 80, 180],    # Indigo
            [187, 19, 62]     # Burgundy
        ]
        # Normalize RGB values to 0-1 range for matplotlib
        self.normalized_colors = [[r/255, g/255, b/255] for r, g, b in self.colors]
        self.index = 0
    
    def __iter__(self):
        """Return self as iterator"""
        self.index = 0  # Reset index
        return self
    
    def __next__(self):
        """Get the next color"""
        if self.index >= len(self.colors):
            raise StopIteration
        
        color = self.normalized_colors[self.index]
        self.index += 1
        return color
    
    def next_color(self):
        """Get the next color. If all colors have been enumerated, restart from beginning."""
        if self.index >= len(self.colors):
            self.index = 0
        
        color = self.normalized_colors[self.index]
        self.index += 1
        return color
    
    def get_hex_color(self):
        """Get color in hexadecimal format, commonly used for web and some visualization libraries"""
        rgb = self.next_color()
        return to_hex(rgb)
    
    def get_rgb_int(self):
        """Get the original RGB integer format"""
        idx = self.index - 1 if self.index > 0 else len(self.colors) - 1
        return self.colors[idx]
    
    def get_current_color_name(self):
        """Get the name of the current color (for labeling)"""
        color_names = [
            "Red", "Magenta", "Teal", "Orange", "Blue", "Yellow",
            "Black", "Sky Blue", "Amber", "Dark Green",
            "Purple", "Gray", "Brown", "Indigo", "Burgundy"
        ]
        idx = self.index - 1 if self.index > 0 else len(self.colors) - 1
        return color_names[idx]


def main():
    """Draw 10 curves to test the color enumerator"""
    # Create a new figure
    plt.figure(figsize=(10, 6))
    
    # Create a color enumerator
    color_enum = ColorEnumerator()
    
    # Generate some data and 10 different curves
    x = np.linspace(0, 10, 100)
    
    # Draw 10 different curves
    for i in range(10):
        # Get the next color
        color = color_enum.next_color()
        color_name = color_enum.get_current_color_name()
        
        # Create slightly different curve functions
        y = np.sin(x + i*0.5) * (i*0.2 + 1)
        
        # Plot the curve and set labels
        plt.plot(x, y, color=color, linewidth=2, label=f'Curve {i+1} ({color_name})')
    
    # Add title and labels
    plt.title('Scientific Paper Color Enumerator Test')
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    
    # Display the figure
    plt.tight_layout()
    plt.savefig('scientific_color_test.png', dpi=300)  # Save high-quality image
    plt.show(block=False)  # Show the plot without blocking the script
    plt.pause(5)  # Pause for 5 seconds to view the plot


# Execute main function
if __name__ == "__main__":
    main()
    
    # Additional demo: Print all colors' RGB values and hex values
    print("\nScientific Paper Color Table:")
    color_enum = ColorEnumerator()
    for i in range(len(color_enum.colors)):
        color = color_enum.next_color()
        hex_color = to_hex(color)
        rgb_int = color_enum.get_rgb_int()
        color_name = color_enum.get_current_color_name()
        print(f"{i+1:2d}. {color_name:8s}: RGB={rgb_int} Hex={hex_color}")