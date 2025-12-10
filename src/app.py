
"""
Manufacturing Data Platform – App Runner
----------------------------------------
Purpose:
  Single entry point to demonstrate:
    • Task 2: SQL queries via src/queries.py
    • Task 3: Python DAL functions via src/dal.py

Run:
  python src/app.py
"""

from queries import (
    product_output_by_month,
    list_wip,
    machine_utilization_simple,
    work_orders_no_production,
    top_scrap_by_product,
    top_scrap_by_machine,
)
from dal import (
    get_product_summary,
    get_wip_orders,
    get_machine_utilization,
    create_work_order,
)

def print_header(text: str):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_rows(rows):
    if not rows:
        print("(no results)")
        return
    for r in rows:
        print(r)

def main():
    print("=== Manufacturing Data Platform – Demo ===")

    # ---------------------------
    # Task 2: SQL Query Wrappers
    # ---------------------------

    print_header("[Task 2.1] Product output by month (2025-12)")
    rows = product_output_by_month("2025-12")
    print_rows(rows)

    print_header("[Task 2.2] Work-in-progress orders at 2025-12-09T12:00:00Z")
    wip_rows = list_wip("2025-12-09T12:00:00Z")
    print_rows(wip_rows)

    print_header("[Task 2.3] Machine utilization (simple) [2025-12-07 .. 2025-12-09]")
    util_simple = machine_utilization_simple("2025-12-07T00:00:00Z", "2025-12-09T23:59:59Z")
    print_rows(util_simple)

    print_header("[Task 2.4] Work orders with no production yet")
    none_ops = work_orders_no_production()
    print_rows(none_ops)

    print_header("[Task 2.5A] Top scrap drivers by product [2025-12-07 .. 2025-12-09]")
    ts_prod = top_scrap_by_product("2025-12-07T00:00:00Z", "2025-12-09T23:59:59Z")
    print_rows(ts_prod)

    print_header("[Task 2.5B] Top scrap drivers by machine [2025-12-07 .. 2025-12-09]")
    ts_mach = top_scrap_by_machine("2025-12-07T00:00:00Z", "2025-12-09T23:59:59Z")
    print_rows(ts_mach)

    # ---------------------------
    # Task 3: Python DAL
    # ---------------------------

    print_header("[Task 3.1] get_product_summary('Widget A', Dec 7–10)")
    summary = get_product_summary("Widget A", "2025-12-07T00:00:00Z", "2025-12-10T23:59:59Z")
    print(summary)

    print_header("[Task 3.2] get_wip_orders(now=2025-12-09T12:00:00Z)")
    wip = get_wip_orders("2025-12-09T12:00:00Z")
    print_rows(wip)

    print_header("[Task 3.3] get_machine_utilization (adjusted) [2025-12-07 .. 2025-12-09]")
    util_adj = get_machine_utilization("2025-12-07T00:00:00Z", "2025-12-09T23:59:59Z", adjusted=True)
    print_rows(util_adj)

    print_header("[Task 3.4] create_work_order(...)")
    try:
        new_id = create_work_order(
            product_id=1,  # Widget A
            planned_qty=220,
            planned_start="2025-12-12T08:00:00Z",
            planned_end="2025-12-12T16:00:00Z",
            machine_id=1
        )
        print(f"Created new work order id={new_id}")
    except Exception as e:
        print(f"Create work order failed: {e}")

if __name__ == "__main__":
    main()
