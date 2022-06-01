# Calculate how big a certain image is, and return the result with the correspondent unit of measure (b, kb, mb or gb).
def naturalsize(count):
    fcount = float(count)
    k = 1024
    m = k * k
    g = m * k
    if fcount < k:
        return str(count) + 'B'
    if fcount >= k and fcount < m:
        return str(int(fcount / (k/10.0)) / 10.0) + 'KB'
    if fcount >= m and fcount < g:
        return str(int(fcount / (m/10.0)) / 10.0) + 'MB'
    return str(int(fcount / (g/10.0)) / 10.0) + 'GB'
