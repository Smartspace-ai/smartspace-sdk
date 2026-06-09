import smtplib
from unittest.mock import MagicMock, patch

import pytest

from smartspace.core import BlockError
from smartspace.blocks.send_email import SendEmail


def _make_block(**overrides) -> SendEmail:
    block = SendEmail()
    block.smtp_host = "smtp.example.com"
    block.smtp_port = 587
    block.from_address = "sender@example.com"
    block.username = "sender@example.com"
    block.password = "secret"
    block.use_tls = True
    block.use_ssl = False
    block.is_html = False
    block.timeout = 30
    for key, value in overrides.items():
        setattr(block, key, value)
    return block


@pytest.mark.asyncio
async def test_send_email_starttls_flow():
    block = _make_block()
    server = MagicMock()

    with patch("smartspace.blocks.send_email.smtplib.SMTP", return_value=server) as smtp:
        result = await block.send(
            to=["a@example.com"],
            subject="Hello",
            body="Body text",
        )

    smtp.assert_called_once_with("smtp.example.com", 587, timeout=30)
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("sender@example.com", "secret")
    server.send_message.assert_called_once()
    server.quit.assert_called_once()

    assert result.sent is True
    assert result.recipients == ["a@example.com"]
    assert result.subject == "Hello"


@pytest.mark.asyncio
async def test_send_email_combines_recipients():
    block = _make_block()
    server = MagicMock()

    with patch("smartspace.blocks.send_email.smtplib.SMTP", return_value=server):
        result = await block.send(
            to=["a@example.com"],
            subject="Hi",
            body="Body",
            cc=["b@example.com"],
            bcc=["c@example.com"],
        )

    _, kwargs = server.send_message.call_args
    assert kwargs["to_addrs"] == ["a@example.com", "b@example.com", "c@example.com"]
    assert result.recipients == ["a@example.com", "b@example.com", "c@example.com"]


@pytest.mark.asyncio
async def test_send_email_uses_ssl_when_configured():
    block = _make_block(use_ssl=True, smtp_port=465)
    server = MagicMock()

    with (
        patch("smartspace.blocks.send_email.smtplib.SMTP_SSL", return_value=server) as smtp_ssl,
        patch("smartspace.blocks.send_email.smtplib.SMTP") as smtp_plain,
    ):
        await block.send(to=["a@example.com"], subject="S", body="B")

    smtp_ssl.assert_called_once()
    smtp_plain.assert_not_called()
    server.starttls.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_skips_login_without_username():
    block = _make_block(username="", password="")
    server = MagicMock()

    with patch("smartspace.blocks.send_email.smtplib.SMTP", return_value=server):
        await block.send(to=["a@example.com"], subject="S", body="B")

    server.login.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_html_body():
    block = _make_block(is_html=True)
    server = MagicMock()

    with patch("smartspace.blocks.send_email.smtplib.SMTP", return_value=server):
        await block.send(
            to=["a@example.com"],
            subject="S",
            body="<h1>Hi</h1>",
        )

    sent_message = server.send_message.call_args.args[0]
    assert sent_message.get_content_type() == "multipart/alternative"


@pytest.mark.asyncio
async def test_send_email_requires_recipient():
    block = _make_block()

    with pytest.raises(BlockError):
        await block.send(to=[], subject="S", body="B")


@pytest.mark.asyncio
async def test_send_email_wraps_auth_error():
    block = _make_block()
    server = MagicMock()
    server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad creds")

    with patch("smartspace.blocks.send_email.smtplib.SMTP", return_value=server):
        with pytest.raises(BlockError) as exc:
            await block.send(to=["a@example.com"], subject="S", body="B")

    assert "authentication failed" in exc.value.message.lower()
    server.quit.assert_called_once()
