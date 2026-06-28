from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.claim_reprocessing_agent import ClaimReprocessingAgent
from servicenow_client import ServiceNowClient
from config import FLASK_ENV, PORT
from db_operations import get_all_claims, get_claim_by_id, save_claim, seed_claims, migrate_statuses, log_action, get_audit_logs, update_claim_status_and_notes
from database import create_tables
from reprocessing import start_reprocessing, ClaimNotFound, ClaimNotReprocessable


def safe_route(audit_action=None, audit_tool=None):
    """Wrap a route: convert unhandled exceptions to JSON 500. If audit_action
    is given, also write an audit log entry on failure."""
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                if audit_action:
                    log_action(audit_action, audit_tool, 'error', str(e), kwargs.get('claim_id'))
                return jsonify({'error': str(e)}), 500
        return wrapped
    return decorator

app = Flask(__name__)
CORS(app)

create_tables()
seed_claims()
migrate_statuses()

# Initialize agents
claim_agent = ClaimReprocessingAgent()
servicenow = ServiceNowClient()

@app.route('/api/chat', methods=['POST'])
@safe_route()
def chat():
    """Handle chat messages from the frontend"""
    data = request.json
    message = data.get('message', '')
    history = data.get('history', [])

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    response = claim_agent.process_message(message, history)
    return jsonify(response), 200

@app.route('/api/incidents/analysis', methods=['GET'])
@safe_route()
def incidents_analysis():
    """Return a full incident analysis report from ServiceNow"""
    analysis = servicenow.get_incidents_analysis()
    if analysis is None:
        return jsonify({'error': 'Could not reach ServiceNow. Check credentials.'}), 503
    return jsonify(analysis), 200

@app.route('/api/incidents/<number>', methods=['GET'])
@safe_route()
def get_incident(number):
    """Get full details for a single incident by number"""
    incident = servicenow.get_incident_by_number(number)
    if not incident:
        return jsonify({'error': f'Incident {number} not found'}), 404
    return jsonify({'incident': incident}), 200

@app.route('/api/incidents/search', methods=['POST'])
@safe_route()
def search_incidents():
    """Search for incidents in ServiceNow"""
    data = request.json
    query = data.get('query', '')
    search_type = data.get('search_type', 'incident_number')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    incidents = servicenow.search_incidents(query, search_type)
    if not incidents:
        return jsonify({
            'incidents': [],
            'message': 'No incidents found. Please check your ServiceNow credentials and configuration.'
        }), 200
    return jsonify({'incidents': incidents, 'count': len(incidents)}), 200

@app.route('/api/claims', methods=['GET'])
@safe_route()
def api_get_claims():
    """Get all claims"""
    return jsonify({'claims': get_all_claims()}), 200

@app.route('/api/claims/<claim_id>/reprocess', methods=['POST'])
@safe_route('reprocess', 'dashboard')
def api_reprocess_claim(claim_id):
    """Reprocess a specific claim — only allowed when status is Processing."""
    try:
        start_reprocessing(claim_id, 'dashboard')
    except ClaimNotFound:
        return jsonify({'error': f'Claim {claim_id} not found'}), 404
    except ClaimNotReprocessable as e:
        return jsonify({'error': f'Only claims with status "EDI Processing" can be reprocessed (current: {e.current_status})'}), 400
    return jsonify({'message': f'Claim {claim_id} is being reprocessed. Status will update to EDI Complete in 10 seconds.'}), 200

@app.route('/api/claims/<claim_id>/fake-reprocess', methods=['POST'])
@safe_route('fake-reprocess', 'fake-api')
def api_fake_reprocess_claim(claim_id):
    """Fake external reprocessing API — immediately marks claim as Processed."""
    claim = get_claim_by_id(claim_id)
    if not claim:
        return jsonify({'error': f'Claim {claim_id} not found'}), 404
    if claim['status'] not in ('UI Draft', 'EDI Processing'):
        return jsonify({'error': f'Claim {claim_id} cannot be adjusted (current status: {claim["status"]})'}), 400

    update_claim_status_and_notes(claim_id, 'EDI Accepted', 'Adjusted claim accepted by agent')
    log_action('fake-reprocess', 'fake-api', 'success', f'Claim {claim_id} marked as EDI Accepted by fake API', claim_id)

    updated = get_claim_by_id(claim_id)
    return jsonify({
        'message': f'Claim {claim_id} has been processed successfully.',
        'claim_id': claim_id,
        'status': updated['status'],
        'notes': updated['notes'],
        'last_updated': updated['last_updated'],
    }), 200


@app.route('/api/audit-logs', methods=['GET'])
@safe_route()
def api_audit_logs():
    """Get recent audit log entries"""
    return jsonify({'logs': get_audit_logs()[:50]}), 200

@app.route('/api/dashboard/stats', methods=['GET'])
@safe_route()
def get_dashboard_stats():
    """Get dashboard statistics from the database"""
    claims = get_all_claims()
    total_claims    = len(claims)
    ui_draft        = sum(1 for c in claims if c['status'] == 'UI Draft')
    edi_processing  = sum(1 for c in claims if c['status'] == 'EDI Processing')
    edi_complete    = sum(1 for c in claims if c['status'] == 'EDI Complete')
    edi_accepted    = sum(1 for c in claims if c['status'] == 'EDI Accepted')
    success_rate = round(edi_complete / total_claims * 100, 1) if total_claims > 0 else 0

    chart_data = [
        {'status': 'UI Draft',       'count': ui_draft,      'percentage': round(ui_draft       / total_claims * 100, 1) if total_claims else 0},
        {'status': 'EDI Processing', 'count': edi_processing,'percentage': round(edi_processing / total_claims * 100, 1) if total_claims else 0},
        {'status': 'EDI Complete',   'count': edi_complete,  'percentage': round(edi_complete   / total_claims * 100, 1) if total_claims else 0},
        {'status': 'EDI Accepted',   'count': edi_accepted,  'percentage': round(edi_accepted   / total_claims * 100, 1) if total_claims else 0},
    ]
    return jsonify({
        'stats': {
            'total_claims':        total_claims,
            'ui_draft':            ui_draft,
            'edi_processing':      edi_processing,
            'edi_complete':        edi_complete,
            'edi_accepted':        edi_accepted,
            'success_rate':        success_rate,
            'avg_processing_time': '10 seconds',
            'claims_last_24h':     2,
            'active_incidents':    3,
        },
        'chart_data': chart_data,
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': FLASK_ENV,
        'version': '1.0.0'
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Claims Management API',
        'version': '1.0.0',
        'endpoints': {
            'chat': '/api/chat',
            'incidents': '/api/incidents/search',
            'claims': '/api/claims',
            'dashboard': '/api/dashboard/stats',
            'health': '/api/health'
        }
    }), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=FLASK_ENV == 'development', host='0.0.0.0', port=PORT)
