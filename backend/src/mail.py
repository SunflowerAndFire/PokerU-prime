import resend
from pydantic import BaseModel

from .config import Config
resend.api_key = Config.RESEND_API_KEY

class EmailModel(BaseModel):
    '''Email list schema'''
    addresses: list[str]
    
async def send_message(
    recipients: list[str], mail_subject: str, mail_body: str
):
    '''Initalize all necessary params to be sent in Resend email API'''

    params: resend.Emails.SendParams = {
        "from": "PokerU <onboarding@resend.dev>",
        "to": recipients,
        "subject": mail_subject,
        "html": mail_body,
        "reply_to": "pokerufromtulane@gmail.com",
    }

    email = resend.Emails.send(params)
    return email
