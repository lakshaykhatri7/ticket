# ============================================================
#  step4_post_tickets.py
#  Allocated tickets ko API ke through engineers ko assign karta hai
#  Har assignment ka result Excel mein save hota hai
#  Output: assignment_result_ddmmyy_hhmmss.xlsx
# ============================================================

import requests
import pandas as pd
from datetime import datetime
from config import API_URL, API_KEY, ORG_ID, INSTANCE, WORKGROUP, ASSIGNED_EMAIL


def post_tickets(allocation, ticket_numbers):
    """
    Har solver ko unke allocated tickets assign karta hai via API.

    Args:
        allocation    (dict): { person_name : ticket_count }
        ticket_numbers (list): step1 se aaye ticket numbers
    """

    print("\n" + "="*55)
    print("  STEP 4 : Tickets API se Post kar raha hoon")
    print("="*55)

    if not allocation:
        print("  ⚠️  Allocation khaali hai. Kuch post karne ko nahi.")
        return

    if not ticket_numbers:
        print("  ⚠️  Ticket numbers nahi mile. Step 1 check karo.")
        return

    # ---- Tickets ko solvers mein distribute karo (round-robin style) ----
    ticket_pool  = list(ticket_numbers)
    assign_map   = {}   # { name : [ticket_no, ...] }
    idx = 0

    for name, count in allocation.items():
        chunk = ticket_pool[idx : idx + count]
        assign_map[name] = chunk
        idx += count

        if idx >= len(ticket_pool):
            print(f"  ⚠️  Tickets khatam ho gayi pool mein. Baaki skip hongi.")
            break

    print(f"\n  Assignment Plan:")
    for name, tlist in assign_map.items():
        print(f"  {name:<25} → {tlist}")

    # ---- API Calls ----
    results = []

    for engineer, tickets in assign_map.items():
        for ticket_no in tickets:

            print(f"\n  🔄 Posting Ticket {ticket_no} → {engineer} ...")

            payload = {
                "ServiceName": "IM_LogOrUpdateIncident",
                "objCommonParameters": {
                    "_ProxyDetails": {
                        "AuthType": "APIKEY",
                        "APIKey": API_KEY,
                        "ProxyID": 0,
                        "ReturnType": "JSON",
                        "OrgID": ORG_ID
                    },
                    "incidentParamsJSON": {
                        "IncidentContainerJsonObj": {
                            "Updater": "Executive",
                            "Ticket": {
                                "IsFromWebService": True,
                                "Ticket_No": ticket_no,
                                "Sup_Function": INSTANCE,
                                "Status": "Assigned",
                                "Assigned_WorkGroup_Name": WORKGROUP,
                                "Medium": "API",
                                "Source": "API Call",
                                "Assigned_Engineer_Email": ASSIGNED_EMAIL,
                                "PageName": "LogTicket"
                            },
                            "TicketInformation": {
                                "Information": f"Auto-assigned to {engineer} via Python"
                            },
                            "CustomFields": []
                        }
                    },
                    "RequestType": "RemoteCall"
                }
            }

            try:
                resp = requests.post(API_URL, json=payload, timeout=30)

                if resp.status_code == 200:
                    print(f"  ✅ Success — Ticket {ticket_no} assigned.")
                    result_status = "Success"
                else:
                    print(f"  ❌ Failed ({resp.status_code}) — Ticket {ticket_no}")
                    result_status = f"Failed_{resp.status_code}"

                results.append({
                    "Ticket_No"        : ticket_no,
                    "Engineer"         : engineer,
                    "Status_Code"      : resp.status_code,
                    "Result"           : result_status,
                    "Assigned by Bot"  : "Yes",
                    "Time"             : datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                })

            except requests.exceptions.ConnectionError:
                print(f"  ❌ Connection error — Ticket {ticket_no}")
                results.append({
                    "Ticket_No"        : ticket_no,
                    "Engineer"         : engineer,
                    "Status_Code"      : "N/A",
                    "Result"           : "Connection Error",
                    "Assigned by Bot"  : "Yes",
                    "Time"             : datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                })

            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({
                    "Ticket_No"        : ticket_no,
                    "Engineer"         : engineer,
                    "Status_Code"      : "N/A",
                    "Result"           : f"Error: {str(e)}",
                    "Assigned by Bot"  : "Yes",
                    "Time"             : datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                })

    # ---- Result Excel save karo ----
    if results:
        ts          = datetime.now().strftime("%d%m%y_%H%M%S")
        result_file = f"assignment_result_{ts}.xlsx"
        pd.DataFrame(results).to_excel(result_file, index=False)
        print(f"\n  ✅ Assignment result saved → {result_file}")

        # ---- Summary print ----
        success = sum(1 for r in results if r["Result"] == "Success")
        failed  = len(results) - success
        print(f"\n  ── POST SUMMARY ─────────────────────────────")
        print(f"  Total Posted : {len(results)}")
        print(f"  ✅ Success   : {success}")
        print(f"  ❌ Failed    : {failed}")


# ---- Standalone run ----
if __name__ == "__main__":
    # Test data
    sample_allocation = {"JYOTI": 3, "AKSHITA": 5}
    sample_tickets    = ["653501", "653502", "653503", "653504", "653505",
                         "653506", "653507", "653508"]
    post_tickets(sample_allocation, sample_tickets)
