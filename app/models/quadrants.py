positions = {
    "left": [
        [2, 2, 2],
        [1, 5, 3],
        [4, 4, 4]],
    "up": [
        [6, 7, 8],
        [9, 10, 11],
        [12, 13, 14]],
    "right": [
        [16, 16, 16],
        [15, 19, 17],
        [18, 18, 18]
    ]
}


def get_quadrant(camera, quadrant):
    position = []
    if camera == 0:
        position = positions['left']
    elif camera == 1:
        position = positions['up']
    elif camera == 2:
        position = positions['right']

    flatten = sum(position, [])
    return flatten[quadrant - 1]

