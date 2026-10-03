TOOLS = ["profile_table", "filter_rows", "aggregate"]
WRITES = ("delete", "drop", "update", "insert")

def run(goal, rows):
    if any(word in goal.lower() for word in WRITES):
        return {"refused": True, "reason": "This agent only reads the table.", "tools": [], "wrote": False}
    profile = {"rows": len(rows), "columns": list(rows[0]) if rows else []}
    totals = {}
    for row in rows:
        totals[row["region"]] = totals.get(row["region"], 0) + row["revenue"]
    return {"refused": False, "tools": TOOLS, "profile": profile, "revenue_by_region": totals, "wrote": False}
