def extract_hidden(path):
    with open(path, "rb") as f:
        data = f.read().decode("utf-8", errors="ignore")

    bits = []
    for ch in data:
        if ch == "\u200b":  # zero width space
            bits.append("0")
        elif ch == "\u200c":  # zero width non-joiner
            bits.append("1")
        elif ch == "\u200d":  # sometimes used
            bits.append("1")

    # group bits into bytes
    secret = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            secret += chr(int("".join(byte), 2))
    return secret

print(extract_hidden("poop_challenge.txt"))
