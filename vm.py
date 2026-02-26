BYTES = 524288
WORD = 512
FRAMES = BYTES // WORD

PM = [0] * BYTES
D = [[0] * WORD for _ in range(FRAMES)]


def st_size (s: int) -> int:
    return s * 2


def st_frame (s: int) -> int:
    return s * 2 + 1


def starting_addr (frame: int) -> int:
    return frame * WORD


def int_extract (va: int) -> tuple:
    s  = (va >> 18) & 0x1FF
    p  = (va >> 9)  & 0x1FF
    w  =  va        & 0x1FF
    pw =  va        & 0x3FFFF
    return s, p, w, pw

_free_frames: list = []

def _build_free_list(used: set):
    used = used | {0, 1}
    _free_frames[:] = [f for f in range(FRAMES) if f not in used]


def alloc_frame () -> int:
    if not _free_frames:
        raise RuntimeError("No free frames available")
    return _free_frames.pop(0)


def init (init_file: str = "init-dp.txt"):
    with open(init_file, "r") as fh:
        line1_tokens = fh.readline().split()
        line2_tokens = fh.readline().split()

    used: set = set()
    seg_pt_frames: dict = {}

    n1 = len(line1_tokens) // 3
    for i in range(n1):
        s      = int(line1_tokens[i * 3])
        length = int(line1_tokens[i * 3 + 1])
        frame  = int(line1_tokens[i * 3 + 2])

        PM[st_size(s)]  = length
        PM[st_frame(s)] = frame
        seg_pt_frames[s] = frame

        if frame >= 0:
            used.add(frame)

    n2 = len(line2_tokens) // 3
    for i in range(n2):
        s  = int(line2_tokens[i * 3])
        p  = int(line2_tokens[i * 3 + 1])
        f2 = int(line2_tokens[i * 3 + 2])

        if f2 >= 0:
            used.add(f2)

        pt_frame = seg_pt_frames.get(s)
        if pt_frame is None:
            continue

        if pt_frame >= 0:
            PM[starting_addr(pt_frame) + p] = f2
        else:
            disk_block = abs(pt_frame)
            D[disk_block][p] = f2

    _build_free_list(used)


def translate (va: int) -> int:
    s, p, w, pw = int_extract(va)

    seg_size = PM[st_size(s)]

    if seg_size == 0:
        return -1

    if pw >= seg_size:
        return -1

    pt_frame = PM[st_frame(s)]

    if pt_frame < 0:
        disk_block = abs(pt_frame)
        new_pt_frame = alloc_frame()
        base = starting_addr(new_pt_frame)
        for i in range(WORD):
            PM[base + i] = D[disk_block][i]
        PM[st_frame(s)] = new_pt_frame
        pt_frame = new_pt_frame

    frame = PM[starting_addr(pt_frame) + p]

    if frame < 0:
        disk_block = abs(frame)
        new_frame = alloc_frame()
        base = starting_addr(new_frame)
        for i in range(WORD):
            PM[base + i] = D[disk_block][i]
        PM[starting_addr(pt_frame) + p] = new_frame
        frame = new_frame

    return starting_addr(frame) + w


def main (init_file: str = "init-dp.txt",
        input_file: str = "input-dp.txt",
        output_file: str = "output-dp.txt"):

    init(init_file)

    with open(input_file, "r") as fh:
        vas = fh.read().split()

    results = []
    for token in vas:
        pa = translate(int(token))
        results.append(str(pa))

    out_str = " ".join(results)
    with open(output_file, "w") as fh:
        fh.write(out_str + "\n")


if __name__ == "__main__":
    main()
