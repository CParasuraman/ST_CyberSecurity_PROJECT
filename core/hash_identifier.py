HASH_SIGNATURES = {
    32:  ["md5", "md4", "ntlm"],
    40:  ["sha1"],
    56:  ["sha224"],
    64:  ["sha256"],
    96:  ["sha384"],
    128: ["sha512"],
}

def identify_hash(hash_value):
    """Returns best-guess algorithm name from hash length."""
    h = hash_value.strip().lower()
    length = len(h)
    candidates = HASH_SIGNATURES.get(length, [])
    return candidates[0] if candidates else "unknown"

def identify_all(hashes):
    """Returns list of (hash, detected_algo) tuples."""
    return [(h, identify_hash(h)) for h in hashes]