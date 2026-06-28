import threading

from database import get_connection
from db_operations import get_claim_by_id, log_action

REPROCESS_DELAY_SECONDS = 10.0


class ClaimNotFound(Exception):
    pass


class ClaimNotReprocessable(Exception):
    def __init__(self, current_status):
        self.current_status = current_status
        super().__init__(f"status is '{current_status}'")


def start_reprocessing(claim_id, source):
    """Schedule EDI Complete for a claim already in EDI Processing state.

    Raises ClaimNotFound / ClaimNotReprocessable on invalid input.
    """
    claim = get_claim_by_id(claim_id)
    if not claim:
        raise ClaimNotFound(claim_id)
    if claim['status'] != 'EDI Processing':
        raise ClaimNotReprocessable(claim['status'])

    log_action('reprocess', source, 'success', f'Claim {claim_id} reprocessing started', claim_id)

    t = threading.Timer(REPROCESS_DELAY_SECONDS, _complete_reprocessing, args=[claim_id, source])
    t.daemon = True
    t.start()


def _complete_reprocessing(claim_id, source):
    """Background task: mark claim EDI Complete if still EDI Processing."""
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE claim SET status='EDI Complete', last_updated=datetime('now') WHERE id=? AND status='EDI Processing'",
            (claim_id,),
        )
        conn.commit()
        conn.close()
        log_action('complete', source, 'success', f'Claim {claim_id} EDI Complete after processing', claim_id)
    except Exception as e:
        log_action('complete', source, 'error', str(e), claim_id)
