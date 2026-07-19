"""Order summary rendering for account exports."""

from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    status: str
    total: float


# A slice of production-ish data: account 1001 has settled orders,
# account 4821 has orders but none of them settled yet.
ACCOUNTS = {
    1001: [
        Order("ord-101", "SETTLED", 40.00),
        Order("ord-102", "PENDING", 12.50),
        Order("ord-103", "SETTLED", 19.99),
    ],
    4821: [
        Order("ord-410", "PENDING", 75.00),
        Order("ord-411", "PENDING", 8.25),
    ],
}


def summarize(orders):
    return [o for o in orders if o.status == "SETTLED"]


def render(first, rows):
    lines = [f"latest settled order: {first.order_id}"]
    total = sum(o.total for o in rows)
    lines.append(f"{len(rows)} settled orders, total ${total:.2f}")
    return "\n".join(lines)


def render_summary(orders):
    rows = summarize(orders)
    first = rows[0]
    return render(first, rows)


def main(account_id):
    print(f"account {account_id}")
    print(render_summary(ACCOUNTS[account_id]))


if __name__ == "__main__":
    import sys

    main(int(sys.argv[1]))
