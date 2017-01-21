
def resize_proportional(width, height, width_max, height_max=None):
    width = float(width)
    height = float(height)
    if width > width_max:
        height *= width_max/width
        width *= width_max/width
    if height_max is not None and height > height_max:
        width *= height_max/height
        height *= height_max/height
    return int(round(width)), int(round(height))

# vim: et:sta:bs=2:sw=4:
