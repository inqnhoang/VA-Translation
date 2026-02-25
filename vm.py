BYTES = 524288
WORD = 512
FRAMES = BYTES / WORD

PM = [0] * 524288
D = [[0] for _ in range(1024) for _ in range(512)]

def st_size (s: int) -> int:
    return s * 2

def st_frame (s: int) -> int:
    return s * 2 + 1

def starting_addr (n: int) -> int:
    return n * 512

def page (s: int, p: int) -> int:
    frame = PM[st_frame(s)]
    return PM[starting_addr(frame) + p]

def va (s: int, p: int, w: int) -> int:
    frame = page(s, p)
    return starting_addr(frame) + w

def int_extract(n: int) -> tuple:
    return ()