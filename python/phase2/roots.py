def bisection(f, lo, hi, tol=1e-12):
    steps = 0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:     # sign change in the left half?
            hi = mid
        else:
            lo = mid
        steps += 1
    return (lo + hi) / 2, steps

# lambda x: x**2 - 2       # is the same as:   def f(x): return x**2 - 2
# root, steps = bisection(lambda x: x**2 - 2, 1, 2)
# print(f"√2 ≈ {root:.12f} in {steps} steps")

def newton(f, df, x, tol = 1e-12, max_step = 50):
    for step in range(1, max_step + 1):
        x_new = x-f(x)/df(x)
        if abs(f(x_new) - f(x)) <= tol:
            return x_new, step
        x = x_new
    return x, max_step

if __name__ == "__main__":
    f = lambda x: x**2 - 2
    df = lambda x: 2*x
    x = 1.0
    root, steps = newton(f, df, x)
    print(f"√2 ≈ {root:.12f} in {steps} steps")

