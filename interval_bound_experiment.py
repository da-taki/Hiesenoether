"""
Interval Bound Collapse Experiment
===================================
Question: For a fixed multiset of L additive steps and m inspect operations,
does the per-site inspect interval [m_lo, m_hi] collapse to [0, m] everywhere
(useless global bound) or stay tight for certain program structures?

We brute-force all permutations of the multiset, compute how many inspects
precede each access site in each permutation, then report [m_lo, m_hi] per site.
"""

from itertools import permutations

def run_experiment(L, m):
    """
    L: number of additive steps (ACCESS operations)
    m: number of inspect operations (INSPECT operations)
    
    We enumerate all unique permutations of the multiset
    ['ACCESS'] * L + ['INSPECT'] * m and for each permutation,
    track how many INSPECTs have occurred before each ACCESS.
    
    Returns per-site intervals [m_lo, m_hi] across all permutations.
    """
    ops = ['ACCESS'] * L + ['INSPECT'] * m
    
    # per-site: for access site k (0-indexed), what values of inspect_count_before_access_k occur?
    # access_site_counts[k] = set of inspect counts seen before the k-th access
    access_site_counts = [set() for _ in range(L)]
    
    seen = set()
    total_perms = 0
    unique_perms = 0

    for perm in permutations(ops):
        total_perms += 1
        key = tuple(perm)
        if key in seen:
            continue
        seen.add(key)
        unique_perms += 1

        inspect_count = 0
        access_index = 0
        for op in perm:
            if op == 'INSPECT':
                inspect_count += 1
            else:  # ACCESS
                access_site_counts[access_index].add(inspect_count)
                access_index += 1

    print(f"\n{'='*60}")
    print(f"L={L} additive steps, m={m} inspect operations")
    print(f"Total permutations: {total_perms}, Unique: {unique_perms}")
    print(f"{'='*60}")
    print(f"{'Access Site':<14} {'m_lo':<8} {'m_hi':<8} {'Range':<8} {'Collapsed?'}")
    print(f"{'-'*60}")

    all_collapsed = True
    for k, counts in enumerate(access_site_counts):
        m_lo = min(counts)
        m_hi = max(counts)
        rng = m_hi - m_lo
        collapsed = (m_lo == 0 and m_hi == m)
        if not collapsed:
            all_collapsed = False
        print(f"Access {k:<7} {m_lo:<8} {m_hi:<8} {rng:<8} {'YES [0,m]' if collapsed else 'NO - TIGHT'}")

    print(f"\nVerdict: {'ALL intervals collapse to [0,m] -- bound is USELESS' if all_collapsed else 'SOME intervals are TIGHT -- bound has value'}")
    return access_site_counts


def run_all():
    print("INTERVAL BOUND COLLAPSE EXPERIMENT")
    print("Does per-site [m_lo, m_hi] collapse to [0, m] everywhere?")
    print("If yes: flow-insensitive interval abstraction is useless.")
    print("If no: tighter static bounds are achievable for some sites.")

    configs = [
        (3, 1),   # small: 3 accesses, 1 inspect
        (4, 1),   # 4 accesses, 1 inspect
        (4, 2),   # 4 accesses, 2 inspects
        (5, 1),   # 5 accesses, 1 inspect
        (5, 2),   # 5 accesses, 2 inspects
        (6, 1),   # matching paper's baseline config
        (6, 2),
    ]

    results = {}
    for L, m in configs:
        site_counts = run_experiment(L, m)
        
        # check which sites are tight
        tight_sites = []
        for k, counts in enumerate(site_counts):
            m_lo = min(counts)
            m_hi = max(counts)
            if not (m_lo == 0 and m_hi == m):
                tight_sites.append((k, m_lo, m_hi))
        
        results[(L, m)] = tight_sites

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for (L, m), tight in results.items():
        if tight:
            print(f"L={L}, m={m}: {len(tight)} tight site(s): {tight}")
        else:
            print(f"L={L}, m={m}: ALL collapsed to [0,{m}] -- useless")

    print("\nINTERPRETATION:")
    print("First and last access sites are structurally constrained:")
    print("  - First access (k=0): m_hi < m always (no inspect can precede it in some orderings)")
    print("  - Last access (k=L-1): m_lo > 0 always (some inspect must precede it in some orderings)")
    print("Middle sites: likely collapse to [0, m]")
    print("\nThis suggests boundary-sensitive analysis might recover tight bounds")
    print("at first/last access sites even when middle sites collapse.")


def tight_combinatorial_bounds(L, m):
    """
    Without enumerating permutations, derive the tight [m_lo, m_hi]
    for each access site k purely from the multiset structure.
    
    For access site k (0-indexed) in a sequence of L accesses and m inspects:
    - Total operations = L + m
    - Access k occupies some position p in the full sequence (0-indexed)
    - Minimum inspects before access k: max(0, p - k) where p is minimized
      The earliest access k can appear is position k (all prior ops are accesses)
      So m_lo = max(0, k - k) = 0. Always 0.
    - Maximum inspects before access k: min(m, p - k) where p is maximized
      The latest access k can appear is position k + m (all m inspects before it)
      So m_hi = min(m, m) = m. Always m.
    
    This proves analytically that [m_lo, m_hi] = [0, m] for every site k,
    regardless of L and m, as long as ordering is unconstrained.
    """
    print(f"\nTIGHT COMBINATORIAL BOUNDS (analytic) for L={L}, m={m}")
    print(f"For access site k in an unconstrained multiset of {L} accesses + {m} inspects:")
    print(f"  Earliest position of access k: k (all prior ops are accesses)")
    print(f"  Latest position of access k:   k + m (all m inspects appear before it)")
    print(f"  Therefore m_lo = 0, m_hi = m for ALL sites k in [0, {L-1}]")
    print(f"  Tight bound = [0, {m}] everywhere. Collapse is STRUCTURAL, not empirical.")
    print(f"  Proof: independent of L, holds for any L >= 1, m >= 0.")


def run_all():
    print("INTERVAL BOUND COLLAPSE EXPERIMENT")
    print("Does per-site [m_lo, m_hi] collapse to [0, m] everywhere?")
    print("If yes: flow-insensitive interval abstraction is useless.")
    print("If no: tighter static bounds are achievable for some sites.")

    configs = [
        (3, 1),
        (4, 1),
        (4, 2),
        (5, 1),
        (5, 2),
        (6, 1),
        (6, 2),
    ]

    results = {}
    for L, m in configs:
        site_counts = run_experiment(L, m)
        tight_sites = []
        for k, counts in enumerate(site_counts):
            m_lo = min(counts)
            m_hi = max(counts)
            if not (m_lo == 0 and m_hi == m):
                tight_sites.append((k, m_lo, m_hi))
        results[(L, m)] = tight_sites

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for (L, m), tight in results.items():
        if tight:
            print(f"L={L}, m={m}: {len(tight)} tight site(s): {tight}")
        else:
            print(f"L={L}, m={m}: ALL collapsed to [0,{m}] -- useless")

    print("\n" + "="*60)
    print("ANALYTIC PROOF OF COLLAPSE")
    print("="*60)
    tight_combinatorial_bounds(6, 1)
    tight_combinatorial_bounds(6, 2)

    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    print("Collapse is not an artifact of small L or m.")
    print("It follows directly from unconstrained ordering:")
    print("  - For any access site k, placing all m inspects before it is always valid.")
    print("  - Placing all m inspects after it is always valid.")
    print("  - Therefore [m_lo, m_hi] = [0, m] for every site, for any L and m.")
    print("Flow-insensitive interval abstraction cannot work for this language.")
    print("The only escape is ordering constraints in the language itself,")
    print("or a different analysis target (e.g., bounding total drift over all permutations,")
    print("not per-site drift for a fixed permutation).")


if __name__ == "__main__":
    run_all()