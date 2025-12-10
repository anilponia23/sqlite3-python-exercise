
# src/app.py

from dal import (
    get_product_summary,
    get_wip_orders,
    get_machine_utilization,
    create_work_order,
)

def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def main():
    print("=== Manufacturing Data Platform (Step 3: Python Data Access Layer) ===")

    # 1) Product summary for a product in a date range
    print_section("[1] get_product_summary(product_name, start_date, end_date)")
    try:
        summary = get_product_summary("Widget A",
                                      "2025-12-07T00:00:00Z",
                                      "2025-12-10T23:59:59Z")
        print("Product summary for 'Widget A' (Dec 7–10):")
        print(summary)
    except Exception as e:
        print("Error:", e)

    # 2) WIP orders at a given 'now'
    print_section("[2] get_wip_orders(now)")
    try:
        wip = get_wip_orders("2025-12-09T12:00:00Z")
        print("Work-in-progress orders at 2025-12-09T12:00:00Z:")
        for r in wip:
            print(r)
    except Exception as e:
        print("Error:", e)

    # 3) Machine utilization in a date range (adjusted subtracts downtime)
    print_section("[3] get_machine_utilization(start_date, end_date)")
    try:
        util = get_machine_utilization("2025-12-07T00:00:00Z",
                                       "2025-12-09T23:59:59Z",
                                       adjusted=True)
        print("Machine utilization (Dec 7–9, adjusted for downtime):")
        for m in util:
            print(m)
    except Exception as e:
        print("Error:", e)

    # 4) Create a new planned work order
    print_section("[4] create_work_order(product_id, planned_qty, planned_start, planned_end, machine_id)")
    try:
        new_id = create_work_order(
            product_id=1,                # Widget A
            planned_qty=220,
            planned_start="2025-12-12T08:00:00Z",
            planned_end="2025-12-12T16:00:00Z",
            machine_id=1
        )
        print(f"Created new work order id={new_id}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
