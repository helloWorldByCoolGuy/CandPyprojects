"""
Game Theory Analysis: Australian Banking Oligopoly

Author: Mahmudunnabi Siam (2026)
using paper Chincarini (2003)

This simulation models price competition between CBA, Westpac,
ANZ, and NAB to demonstrate why price competition is limited
in Australian banking.
"""

import itertools


# ============================================================
# CONFIGURATION
# ============================================================

BANKS = ["CBA", "Westpac", "ANZ", "NAB"]
STRATEGIES = ["Cut", "Keep High"]
QUARTERS = 20


# ============================================================
# PAYOFF FUNCTION
# ============================================================

def calculate_payoff(bank_index, choices):
    """
    Calculate quarterly profit ($B) for a bank given all banks' choices.

    Logic:
    - All keep high: $5.0B each (cooperative outcome)
    - One cuts alone: cutter gets $6.5B, others get $3.5B
    - Two cut: cutters get $4.5B, keepers get $2.5B
    - Three cut: cutters get $3.5B, keeper gets $1.5B
    - All cut: $2.5B each (price war)
    """
    num_cutting = choices.count("Cut")
    i_cut = choices[bank_index] == "Cut"

    payoffs = {
        0: 5.0,
        1: 6.5 if i_cut else 3.5,
        2: 4.5 if i_cut else 2.5,
        3: 3.5 if i_cut else 1.5,
        4: 2.5
    }
    return payoffs[num_cutting]


# ============================================================
# CORE GAME FUNCTIONS
# ============================================================

def generate_all_outcomes():
    """Generate all 16 possible strategy combinations for 4 banks."""
    return list(itertools.product(STRATEGIES, repeat=len(BANKS)))


def get_payoffs(outcome):
    """Get payoff for each bank given an outcome."""
    choices = list(outcome)
    return [calculate_payoff(i, choices) for i in range(len(BANKS))]


def is_nash_equilibrium(outcome):
    """
    Check if an outcome is a Nash Equilibrium.
    No bank can improve its payoff by unilaterally changing strategy.
    """
    choices = list(outcome)
    for bank in range(len(BANKS)):
        current_payoff = calculate_payoff(bank, choices)
        alt_choices = choices.copy()
        alt_choices[bank] = "Keep High" if choices[bank] == "Cut" else "Cut"
        alt_payoff = calculate_payoff(bank, alt_choices)
        if alt_payoff > current_payoff:
            return False
    return True


def find_dominant_strategy(bank_index):
    """
    Check if a bank has a dominant strategy.
    A strategy is dominant if it wins in every possible scenario.
    """
    outcomes = generate_all_outcomes()
    cut_always_wins = True
    keep_always_wins = True

    for outcome in outcomes:
        choices = list(outcome)
        cut_choices = choices[:bank_index] + ["Cut"] + choices[bank_index + 1:]
        keep_choices = choices[:bank_index] + ["Keep High"] + choices[bank_index + 1:]
        cut_payoff = calculate_payoff(bank_index, cut_choices)
        keep_payoff = calculate_payoff(bank_index, keep_choices)

        if cut_payoff < keep_payoff:
            cut_always_wins = False
        if keep_payoff < cut_payoff:
            keep_always_wins = False

    if cut_always_wins:
        return "Cut"
    elif keep_always_wins:
        return "Keep High"
    return None


def check_prisoners_dilemma(ne_payoffs, coop_payoffs):
    """
    Check if Prisoner's Dilemma exists.
    True if cooperative outcome is better for ALL players than NE.
    """
    return all(c > n for c, n in zip(coop_payoffs, ne_payoffs))


def run_grim_trigger(coop_profit, cheat_profit, punish_profit, quarters):
    """
    Simulate grim trigger strategy over multiple quarters.
    Returns list of (quarter, coop_total, cheat_total, difference).
    """
    results = []
    coop_total = 0
    cheat_total = 0

    for q in range(1, quarters + 1):
        coop_total += coop_profit
        cheat_total += cheat_profit if q == 1 else punish_profit
        results.append((q, coop_total, cheat_total, coop_total - cheat_total))

    return results


def find_breakeven_quarter(coop_profit, cheat_profit, punish_profit):
    """Find the first quarter where cooperation becomes more profitable."""
    coop_total = 0
    cheat_total = 0
    for q in range(1, 100):
        coop_total += coop_profit
        cheat_total += cheat_profit if q == 1 else punish_profit
        if coop_total > cheat_total:
            return q
    return None


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def print_outcomes_table(outcomes):
    """Print the 16-outcome table with NE marked."""
    print(f"{'#':<4} {'CBA':<10} {'WBC':<10} {'ANZ':<10} {'NAB':<10}"
          f" | {'CBA':>5} {'WBC':>5} {'ANZ':>5} {'NAB':>5} {'Total':>6}")
    print("-" * 75)

    nash_results = []
    for i, outcome in enumerate(outcomes, 1):
        payoffs = get_payoffs(outcome)
        total = sum(payoffs)
        ne = is_nash_equilibrium(outcome)
        if ne:
            nash_results.append((outcome, payoffs))

        label = lambda s: "Cut" if s == "Cut" else "Keep"
        marker = " <-- NE" if ne else ""
        print(f"{i:<4} {label(outcome[0]):<10} {label(outcome[1]):<10} "
              f"{label(outcome[2]):<10} {label(outcome[3]):<10}"
              f" | {payoffs[0]:>5.1f} {payoffs[1]:>5.1f} "
              f"{payoffs[2]:>5.1f} {payoffs[3]:>5.1f} {total:>6.1f}{marker}")

    return nash_results


def print_grim_trigger(results):
    """Print the quarterly cooperation vs cheating comparison."""
    print(f"{'Quarter':<10} {'Cooperate':>12} {'Cheat':>12} {'Difference':>12}")
    print("-" * 48)
    for q, coop, cheat, diff in results:
        sign = "+" if diff > 0 else ""
        print(f"Q{q:<9} ${coop:>10.1f}B ${cheat:>10.1f}B {sign}${diff:>9.1f}B")


def print_summary(dominant_strategies, ne_outcome, ne_payoffs,
                  coop_payoff, breakeven, grim_results):
    """Print summary with all values from simulation."""
    ne_each = ne_payoffs[0]
    ne_total = sum(ne_payoffs)
    coop_total = len(BANKS) * coop_payoff
    final_diff = grim_results[-1][3]

    print(f"1. Dominant strategy for all banks: "
          f"{dominant_strategies[BANKS[0]]}")
    print(f"   Verified: "
          f"{', '.join(f'{b}={s}' for b, s in dominant_strategies.items())}")
    print()
    print(f"2. Nash Equilibrium: {', '.join(ne_outcome)}")
    print(f"   Each earns ${ne_each}B | Total ${ne_total}B")
    print()
    print(f"3. Prisoner's Dilemma: "
          f"Cooperative ${coop_payoff}B > NE ${ne_each}B")
    print(f"   Industry loses ${coop_total - ne_total}B from non-cooperation")
    print()
    print(f"4. Grim trigger breakeven: Q{breakeven}")
    print(f"   {QUARTERS}-quarter advantage of cooperation: ${final_diff}B")
    print()
    print(f"5. Conclusion: Tacit collusion sustains P > MC")


# ============================================================
# MAIN
# ============================================================

def main():
    outcomes = generate_all_outcomes()
    coop_payoff = 5.0
    cheat_profit = 6.5
    punish_profit = 2.5

    # Part 1: All outcomes and Nash Equilibrium
    print("=" * 60)
    print("4-PLAYER SIMULATION (Figure 2)")
    print("=" * 60)
    print()
    nash_results = print_outcomes_table(outcomes)

    ne_outcome = nash_results[0][0]
    ne_payoffs = nash_results[0][1]
    coop_payoffs = [coop_payoff] * len(BANKS)
    is_pd = check_prisoners_dilemma(ne_payoffs, coop_payoffs)

    print()
    print(f"Nash Equilibrium: {len(nash_results)} found")
    print(f"  {', '.join(ne_outcome)}")
    print(f"  Each earns ${ne_payoffs[0]}B | Total: ${sum(ne_payoffs)}B")
    print()
    print(f"Cooperative: ${coop_payoff}B each | ${sum(coop_payoffs)}B total")
    print(f"Surplus lost: ${sum(coop_payoffs) - sum(ne_payoffs)}B")
    print(f"Prisoner's Dilemma: {'Confirmed' if is_pd else 'Not found'}")

    # Part 2: Repeated game
    print()
    print("=" * 60)
    print("REPEATED GAME: GRIM TRIGGER STRATEGY")
    print("=" * 60)
    print()
    grim_results = run_grim_trigger(
        coop_payoff, cheat_profit, punish_profit, QUARTERS
    )
    print_grim_trigger(grim_results)
    breakeven = find_breakeven_quarter(
        coop_payoff, cheat_profit, punish_profit
    )
    print()
    print(f"Breakeven: Q{breakeven}")
    print(f"After {QUARTERS} quarters cooperation earns "
          f"${grim_results[-1][3]}B more")

    # Part 3: Summary
    dominant_strategies = {
        bank: find_dominant_strategy(i) for i, bank in enumerate(BANKS)
    }
    print()
    print("=" * 60)
    print("SUMMARY (all values calculated from simulation)")
    print("=" * 60)
    print()
    print_summary(
        dominant_strategies, ne_outcome, ne_payoffs,
        coop_payoff, breakeven, grim_results
    )
    print()

    print("- Payoff values are theoretical illustrations")


if __name__ == "__main__":
    main()