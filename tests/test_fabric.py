from fabric.crypto import SharedSecret
from fabric.models import ActionRequest, EventType, RiskLevel
from fabric.node import FabricNode


def test_pairing_encrypts_and_executes_trusted_low_risk_action(tmp_path):
    secret = SharedSecret.new()
    laptop = FabricNode("laptop", secret, tmp_path / "laptop.db")
    phone = FabricNode("phone", secret, tmp_path / "phone.db")
    phone.register("media.play", lambda p: f"playing {p['title']}")

    _, envelope = laptop.request_action(ActionRequest(
        "media.play", {"title": "Blinding Lights"}, RiskLevel.LOW, "phone", trusted=True))
    event, result = phone.receive_envelope(envelope)

    assert event.event_type is EventType.ACTION_REQUEST
    assert result == "playing Blinding Lights"
    assert "Blinding Lights" not in str(envelope)


def test_sensitive_actions_require_approval(tmp_path):
    secret = SharedSecret.new()
    laptop = FabricNode("laptop", secret, tmp_path / "laptop.db")
    phone = FabricNode("phone", secret, tmp_path / "phone.db")
    phone.register("message.send", lambda _: "should not run")
    _, envelope = laptop.request_action(ActionRequest(
        "message.send", {}, RiskLevel.SENSITIVE, "phone", trusted=True))
    _, result = phone.receive_envelope(envelope)
    assert result == "approval_required"


def test_expired_request_is_never_executed(tmp_path):
    secret = SharedSecret.new()
    laptop = FabricNode("laptop", secret, tmp_path / "laptop.db")
    phone = FabricNode("phone", secret, tmp_path / "phone.db")
    phone.register("app.open", lambda _: "should not run")
    event, envelope = laptop.request_action(ActionRequest(
        "app.open", {"package": "com.example"}, RiskLevel.LOW, "phone", expires_in_seconds=-1, trusted=True))
    received, result = phone.receive_envelope(envelope)
    assert received.event_id == event.event_id
    assert result == "expired"
