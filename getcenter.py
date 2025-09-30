import argparse
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

clicked_points = []

def get_center(p1, p2):
    center_x = (p1[0] + p2[0]) / 2
    center_y = (p1[1] + p2[1]) / 2
    return center_x, center_y

def make_on_click(ax, fig, img_np):
    def on_click(event):
        toolbar = plt.get_current_fig_manager().toolbar
        if toolbar.mode != '':
            return  # Skip click if zoom/pan tool active

        if event.inaxes:
            x, y = int(event.xdata), int(event.ydata)
            clicked_points.append((x, y))
            print(f"Clicked: ({x}, {y})")

            ax.plot(x, y, 'ro')
            fig.canvas.draw()

            if len(clicked_points) == 2:
                p1, p2 = clicked_points
                center = get_center(p1, p2)
                print(f"Center of square = ({center[0]:.2f}, {center[1]:.2f})")

                # Draw the square's diagonal and center
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'g-')
                ax.plot(center[0], center[1], 'yx', markersize=10)
                ax.text(center[0], center[1], f"({center[0]:.1f}, {center[1]:.1f})",
                        color='yellow', fontsize=10, ha='left',
                        bbox=dict(facecolor='black', alpha=0.5))
                fig.canvas.draw()

                xlim = ax.get_xlim()
                ylim = ax.get_ylim()

                plt.pause(1)
                ax.clear()
                ax.imshow(img_np, origin='upper')
                ax.set_title("Click two opposite vertices of a square")
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                fig.canvas.draw()

                clicked_points.clear()
    return on_click

def main():
    parser = argparse.ArgumentParser(description="Click two points to define a square and show its center.")
    parser.add_argument("--path", type=str, required=True, help="Path to the image file")
    args = parser.parse_args()

    # Load image
    img = Image.open(args.path)
    img_np = np.array(img)

    fig, ax = plt.subplots()
    ax.imshow(img_np, origin='upper')
    ax.set_title("Click two opposite vertices of a square")
    fig.canvas.mpl_connect('button_press_event', make_on_click(ax, fig, img_np))

    plt.show()

if __name__ == "__main__":
    main()
