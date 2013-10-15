#!/usr/bin/env python
"""Display terminal colors in an array"""

# Show black color on a white background
BLACK_ON_WHITE = False

# 16-colors index table
COLORS16_RGB = [
    0x000000, 0x800000, 0x008000, 0x808000,
    0x000080, 0x800080, 0x008080, 0xc0c0c0,
    0x808080, 0xff0000, 0x00ff00, 0xffff00,
    0x0000ff, 0xff00ff, 0x00ffff, 0xffffff]


def build_colors256():
    """Build a 256-colors index table"""
    # First 16 colors are the same as COLOR16
    colors = [] + COLORS16_RGB

    # Then, 6*6*6 = 216 colors
    colors6 = [0, 95, 135, 175, 215, 255]
    for r in colors6:
        for g in colors6:
            for b in colors6:
                colors.append((r << 16) | (g << 8) | b)

    # 24 shades of gray
    colors += [0x010101 * i for i in range(8, 239, 10)]
    return colors

COLORS256_RGB = build_colors256()
assert(len(COLORS256_RGB) == 256)


def color_index2term(index):
    """Format a color index to a nice terminal representation"""
    if index < 0 or index > 256:
        return ""
    color = COLORS256_RGB[index]
    r, g, b = (color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff

    # Use several escape sequences so that 16-colors appears correctly on
    # non-256color terms
    if index < 8:
        escape = "\033[{}m".format(30 + index)
    elif index < 16:
        escape = "\033[{}m".format(90 - 8 + index)
    else:
        escape = "\033[38;5;{}m".format(index)

    if BLACK_ON_WHITE and r < 10 and g < 10 and b < 10:
        escape += "\033[107m"
    return escape + "{:3d}: {:02x}/{:02x}/{:02x}\033[m".format(
        index, r, g, b)


# Display the table
print("16-colors table:")
for line in range(4):
    print(" ".join([color_index2term(4*line + col) for col in range(4)]))
print("")

print("216-RGB-colors table:")
for line in range(36):
    print(" ".join([color_index2term(6*line + col + 16) for col in range(6)]))
print("")

print("24-gray-colors table:")
for line in range(4):
    print(" ".join([color_index2term(6*line + col + 232) for col in range(6)]))
