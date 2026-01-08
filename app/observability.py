# Stubbed Observability Module (TruLens Disabled)
# This module mocks the interface of the previous TruLens integration
# to prevent ImportErrors in app.rag_qa.

TRULENS_AVAILABLE = False

def get_recorder(chain, app_id="BookSherpa-v4"):
    """No-op recorder. Returns the chain unwrapped."""
    return chain

def launch_dashboard():
    """No-op dashboard launcher."""
    print("⚠️ Observability is disabled.")
    pass

def setup_trulens():
    return []
