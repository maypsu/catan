import matplotlib.pyplot as plt
import numpy as np
from BoardState import BoardState
import Defines as D

HEX_LAYOUT = [
    (0, 0), (1, 0), (2, 0),
    (-0.5, -np.sqrt(3)/2), (0.5, -np.sqrt(3)/2), (1.5, -np.sqrt(3)/2), (2.5, -np.sqrt(3)/2),
    (-1, -np.sqrt(3)), (0, -np.sqrt(3)), (1, -np.sqrt(3)), (2, -np.sqrt(3)), (3, -np.sqrt(3)),
    (-0.5, -1.5*np.sqrt(3)), (0.5, -1.5*np.sqrt(3)), (1.5, -1.5*np.sqrt(3)), (2.5, -1.5*np.sqrt(3)),
    (0, -2*np.sqrt(3)), (1, -2*np.sqrt(3)), (2, -2*np.sqrt(3))
]

HEX_COORDS = [
    (0, -2), (1, -2), (2, -2),
    (-1, -1), (0, -1), (1, -1), (2, -1),
    (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0),
    (-2, 1), (-1, 1), (0, 1), (1, 1),
    (-2, 2), (-1, 2), (0, 2)
]

RESOURCE_COLORS = {
    "Grain": "#f7e58c",
    "Lumber": "#228B22",
    "Brick": "#b22222",
    "Ore": "#a9a9a9",
    "Wool": "#90ee90",
    "Desert": "#f0e68c"
}

def draw_hex(ax, center, size=1, color='white', label=None, text_color='black'):
    x, y = center
    angles = np.linspace(0, 2*np.pi, 7)
    hexagon = np.array([
        (x + size * np.sin(a), y + size * np.cos(a)) for a in angles
    ])
        
    ax.fill(hexagon[:, 0], hexagon[:, 1], color=color, edgecolor='black')
    if label:
        ax.text(x, y, label, ha='center', va='center', fontsize=10, color=text_color)

def draw_board(board, reward):
    resource_types = []
    dice_numbers = []
    N = 2
    for i in range(len(HEX_COORDS)):
        coords = HEX_COORDS[i]
        hex = board.board[coords]
        resource_types.append(D.RESOURCE_PRODUCTION[hex.tile])
        dice_numbers.append(hex.number)

    _, ax = plt.subplots(figsize=(8, 7))
    ax.set_aspect('equal')
    ax.axis('off')

    size = .575
    for i, (x, y) in enumerate(HEX_LAYOUT):
        res = resource_types[i]
        num = dice_numbers[i]
        color = RESOURCE_COLORS.get(res, 'white')
        label = f"{num}" if num is not None else ''
        text_color = 'black' if num != 6 and num != 8 else 'red'  # Highlight good numbers
        draw_hex(ax, (x, y), size=size, color=color, label=label, text_color=text_color)

    for intersection, pname in board.settlements.items():
        (q, r, corner) = intersection.hexCoords[0]
        angle = np.radians(300) + corner * np.radians(60)
        center = HEX_LAYOUT[HEX_COORDS.index((q, r))]
        ax.plot(center[0] + size * np.sin(angle), center[1] + size * np.cos(angle), 'o', color=pname, markersize=10)

    for intersection, pname in board.cities.items():
        (q, r, corner) = intersection.hexCoords[0]
        angle = np.radians(300) + corner * np.radians(60)
        center = HEX_LAYOUT[HEX_COORDS.index((q, r))]
        ax.plot(center[0] + size * np.sin(angle), center[1] + size * np.cos(angle), 'X', color=pname, markersize=10)

    for road, pname in board.roads.items():
        (q, r, edge) = road.hexCoords[0]
        a = np.radians(300) + edge * np.radians(60)
        b = np.radians(300) + ((edge + 1) % 6) * np.radians(60)
        center = HEX_LAYOUT[HEX_COORDS.index((q, r))]
        ax.plot([center[0] + size * np.sin(a), center[0] + size * np.sin(b)], [center[1] + size * np.cos(a), center[1] + size * np.cos(b)], color=pname, linewidth=4)

    plt.title("Settlers of Catan - " + ", ".join(board.players) + " Reward: " + str(reward))
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    players = ["Red", "Blue", "Yellow", "White"]
    board = BoardState(players)

    board.buildSettle("Red", (-2, 1, 3), start=True)
    board.buildRoad("Red", (-2, 1, 3), start=True)

    draw_board(board, 0.0)
