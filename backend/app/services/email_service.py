import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, Disposition, FileContent, FileName, FileType, Mail

from ..core.config import settings


class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.FROM_EMAIL

    def send_report_email(self, to_email: str, book_title: str, author: str, pdf_path: str, plan_type: str):
        """Sends the generated report PDF to the user's email."""

        # Read PDF file
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        # Encode PDF to base64
        encoded_file = base64.b64encode(pdf_data).decode()

        # Create attachment
        attached_file = Attachment(
            FileContent(encoded_file),
            FileName(f"{book_title.replace(' ', '_')}_report.pdf"),
            FileType("application/pdf"),
            Disposition("attachment"),
        )

        # Create email
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=f"Your {plan_type.capitalize()} Report: {book_title}",
            html_content=f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                            Your Screendibs Report is Ready!
                        </h1>
                        
                        <p>Hello,</p>
                        
                        <p>Thank you for using Screendibs! Your <strong>{plan_type.capitalize()}</strong> literary analysis report for:</p>
                        
                        <div style="background-color: #ecf0f1; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
                            <h2 style="margin: 0; color: #2c3e50;">{book_title}</h2>
                            <p style="margin: 5px 0; color: #7f8c8d;">by {author}</p>
                        </div>
                        
                        <p>Your comprehensive report is attached to this email as a PDF document.</p>
                        
                        <p style="margin-top: 30px;">
                            <strong>What's included in your report:</strong>
                        </p>
                        <ul style="color: #555;">
                            <li>Detailed synopsis and analysis</li>
                            <li>Author background</li>
                            <li>Thematic exploration</li>
                            <li>And much more!</li>
                        </ul>
                        
                        <p style="margin-top: 30px;">
                            Need another report? Visit <a href="{settings.FRONTEND_URL}" style="color: #3498db;">Screendibs</a> anytime!
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This email was sent by Screendibs. If you have any questions, please contact us.
                        </p>
                    </div>
                </body>
            </html>
            """,
        )

        # Attach PDF
        message.attachment = attached_file

        # Send email
        try:
            response = self.client.send(message)
            return response.status_code == 202
        except Exception as e:
            raise Exception(f"Failed to send email: {e}")
