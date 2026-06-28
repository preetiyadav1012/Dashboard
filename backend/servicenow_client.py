import requests
from requests.auth import HTTPBasicAuth
from config import SERVICENOW_API_BASE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD

PRIORITY_MAP = {'1': 'Critical', '2': 'High', '3': 'Moderate', '4': 'Low', '5': 'Planning'}
STATE_MAP    = {'1': 'New', '2': 'In Progress', '3': 'On Hold', '6': 'Resolved', '7': 'Closed'}

INCIDENT_PATH = '/table/incident'

ANALYSIS_FIELDS = ('number,short_description,description,state,priority,category,'
                   'sys_created_on,assigned_to,assignment_group,caller_id,sys_id,'
                   'comments_and_work_notes')

SEARCH_QUERY_TEMPLATES = {
    'incident_number':   'number={}',
    'short_description': 'short_descriptionLIKE{}',
    'state':             'state={}',
    'priority':          'priority={}',
}


class ServiceNowClient:
    def __init__(self):
        self.base_url = SERVICENOW_API_BASE
        self.auth = HTTPBasicAuth(SERVICENOW_USERNAME, SERVICENOW_PASSWORD)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _get(self, path, params=None, timeout=10):
        """GET against ServiceNow. Raises for HTTP errors and hibernation;
        returns the 'result' list from the JSON body."""
        response = requests.get(
            f'{self.base_url}{path}',
            params=params,
            auth=self.auth,
            headers=self.headers,
            timeout=timeout,
        )
        response.raise_for_status()
        self._check_hibernating(response)
        return response.json().get('result', [])

    def _check_hibernating(self, response):
        ct = response.headers.get('Content-Type', '')
        if 'text/html' in ct or response.text.strip().startswith('<'):
            raise RuntimeError(
                "ServiceNow instance is hibernating. "
                "Please wake it up at developer.servicenow.com and try again."
            )

    def _label_incident(self, inc):
        """Normalize priority/state codes to human-readable labels."""
        inc = dict(inc)
        p = str(inc.get('priority', ''))
        s = str(inc.get('state', ''))
        inc['priority_label'] = PRIORITY_MAP.get(p, inc.get('priority', 'Unknown'))
        inc['state_label']    = STATE_MAP.get(s,    inc.get('state',    'Unknown'))
        return inc

    def search_incidents(self, query, search_type='incident_number'):
        """Search for incidents in ServiceNow by number, description, state, or priority."""
        template = SEARCH_QUERY_TEMPLATES.get(search_type, SEARCH_QUERY_TEMPLATES['incident_number'])
        try:
            return self._get(INCIDENT_PATH, params={
                'sysparm_query': template.format(query),
                'sysparm_limit': 100,
                'sysparm_display_value': 'true',
            })
        except Exception as e:
            print(f"Error searching incidents: {e}")
            return []

    def get_incidents_analysis(self, limit=100):
        """Fetch recent incidents and return a summary analysis report."""
        try:
            incidents = [self._label_incident(i) for i in self._get(INCIDENT_PATH, params={
                'sysparm_limit': limit,
                'sysparm_fields': ANALYSIS_FIELDS,
                'sysparm_display_value': 'true',
                'sysparm_order_by': 'sys_created_on',
                'sysparm_order_by_direction': 'desc',
            }, timeout=15)]
        except Exception as e:
            print(f"Error fetching incidents analysis: {e}")
            raise

        priority_counts, state_counts, category_counts = {}, {}, {}
        for inc in incidents:
            p = inc['priority_label']
            s = inc['state_label']
            c = inc.get('category') or 'Uncategorized'
            priority_counts[p] = priority_counts.get(p, 0) + 1
            state_counts[s]    = state_counts.get(s, 0) + 1
            category_counts[c] = category_counts.get(c, 0) + 1

        return {
            'total': len(incidents),
            'priority_breakdown': priority_counts,
            'state_breakdown':    state_counts,
            'category_breakdown': category_counts,
            'recent_incidents':   incidents[:10],
        }

    def get_incident_by_number(self, number):
        """Fetch full details for a single incident by its number."""
        try:
            results = self._get(INCIDENT_PATH, params={
                'number': number,
                'sysparm_display_value': 'true',
            })
        except Exception as e:
            print(f"Error fetching incident {number}: {e}")
            return None
        return self._label_incident(results[0]) if results else None
