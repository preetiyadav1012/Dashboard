from db_operations import (
    get_all_incidents,
    get_audit_logs,
    get_summary_report,
    get_all_claims
    
)

from tabulate import tabulate 

 

def view_all_data(): 

    report = get_summary_report() 

 

    # Overview 

    print(tabulate([ 

        ['Total Incidents', report['total_incidents']], 

        ['Total Analyses',  report['total_analyses']], 

        ['Escalations',     report['escalations']], 

    ], headers=['Metric', 'Count'], tablefmt='pretty')) 

 

    # Incidents 

    incidents = get_all_incidents() 

    print(tabulate([ 

        [i['incident_number'], i['title'][:40], 

         i['priority'], i['fetched_at'][:16]] 

        for i in incidents 

    ], headers=['Number','Title','Priority','Time'], 

       tablefmt='pretty')) 



    claims = get_all_claims()
    print(tabulate([
        [
            c.get('claim_id', ''),
            c.get('batch_id', ''),
            c.get('claim_number', ''),
            c.get('claim_state', ''),
            (c.get('member_id', '') or ''),
            (c.get('created_date', '') or '')[:16]
        ]
        for c in claims
    ], headers=['Claim ID', 'Batch ID', 'Claim #', 'State', 'Member ID', 'Created'], tablefmt='pretty'))

 

def view_all_claims():
    claims = get_all_claims()
    from tabulate import tabulate
    if claims:
        print("\nClaims Table:")
        print(tabulate([list(c.values()) for c in claims], headers=claims[0].keys(), tablefmt='pretty'))
    else:
        print("No claims found.")

if __name__ == '__main__': 

    view_all_data()
    view_all_claims()