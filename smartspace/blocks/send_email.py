import asyncio
import smtplib
import ssl
from email.message import EmailMessage
from typing import Annotated, Optional

from pydantic import BaseModel
from smartspace.core import Block, BlockError, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


class EmailResult(BaseModel):
    sent: bool
    recipients: list[str]
    subject: str


@metadata(
    category=BlockCategory.FUNCTION,
    description=(
        "Sends an email over SMTP. Configure the SMTP server, credentials, and "
        "sender once, then provide recipients, subject, and body at run time. "
        "Supports STARTTLS, implicit SSL, CC/BCC, and HTML bodies."
    ),
    icon="fa-envelope",
    label="send email, smtp, email notification, mail, send message, smtplib, email block",
)
class SendEmail(Block):
    smtp_host: Annotated[
        str, Config(), Metadata(description="SMTP server hostname, e.g. smtp.office365.com")
    ]
    smtp_port: Annotated[
        int, Config(), Metadata(description="SMTP server port (587 for STARTTLS, 465 for SSL, 25 plain)")
    ] = 587
    from_address: Annotated[
        str, Config(), Metadata(description="The 'From' email address messages are sent as")
    ]
    username: Annotated[
        str, Config(), Metadata(description="SMTP auth username. Leave empty for unauthenticated servers.")
    ] = ""
    password: Annotated[
        str, Config(), Metadata(description="SMTP auth password or app password")
    ] = ""
    use_tls: Annotated[
        bool, Config(), Metadata(description="Upgrade the connection with STARTTLS after connecting")
    ] = True
    use_ssl: Annotated[
        bool, Config(), Metadata(description="Connect using implicit SSL/TLS (SMTP_SSL). Overrides STARTTLS.")
    ] = False
    is_html: Annotated[
        bool, Config(), Metadata(description="Treat the body as HTML instead of plain text")
    ] = False
    timeout: Annotated[
        int, Config(), Metadata(description="Connection timeout in seconds")
    ] = 30

    @step(output_name="result")
    async def send(
        self,
        to: Annotated[
            list[str], Metadata(description="Primary recipient email addresses")
        ],
        subject: Annotated[str, Metadata(description="Email subject line")],
        body: Annotated[str, Metadata(description="Email body (plain text or HTML)")],
        cc: Annotated[
            Optional[list[str]], Metadata(description="CC recipient email addresses")
        ] = None,
        bcc: Annotated[
            Optional[list[str]], Metadata(description="BCC recipient email addresses")
        ] = None,
    ) -> EmailResult:
        if not self.smtp_host:
            raise BlockError("smtp_host is required")
        if not self.from_address:
            raise BlockError("from_address is required")

        to = to or []
        cc = cc or []
        bcc = bcc or []

        recipients = [address for address in (*to, *cc, *bcc) if address]
        if not recipients:
            raise BlockError("At least one recipient (to, cc, or bcc) is required")

        message = EmailMessage()
        message["From"] = self.from_address
        message["To"] = ", ".join(to)
        if cc:
            message["Cc"] = ", ".join(cc)
        message["Subject"] = subject
        if self.is_html:
            message.set_content(
                "This email requires an HTML-capable email client to view."
            )
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        try:
            await asyncio.to_thread(self._send_message, message, recipients)
        except smtplib.SMTPAuthenticationError:
            raise BlockError(
                "SMTP authentication failed. Check the username and password."
            )
        except smtplib.SMTPException as e:
            raise BlockError(f"Failed to send email: {e}")
        except OSError as e:
            raise BlockError(f"Could not connect to SMTP server {self.smtp_host}:{self.smtp_port}: {e}")

        return EmailResult(sent=True, recipients=recipients, subject=subject)

    def _send_message(self, message: EmailMessage, recipients: list[str]) -> None:
        if self.use_ssl:
            context = ssl.create_default_context()
            server: smtplib.SMTP = smtplib.SMTP_SSL(
                self.smtp_host, self.smtp_port, timeout=self.timeout, context=context
            )
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout)

        try:
            server.ehlo()
            if self.use_tls and not self.use_ssl:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
            if self.username:
                server.login(self.username, self.password)
            server.send_message(
                message, from_addr=self.from_address, to_addrs=recipients
            )
        finally:
            server.quit()
