from dotenv import load_dotenv
import os
import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from api.config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, OPENAI_API_KEY, OPENAI_ORG_ID
from api.model.mailrequest import MailRequest

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Mail"])

load_dotenv()

# Shared mailbox address for receiving ideas
SHARED_MAILBOX = "idea@angermeier.net"

# Import verify_api_key at runtime to avoid circular dependency
def get_verify_api_key():
    from api.main import verify_api_key
    return verify_api_key

async def get_graph_token():
    """
    Get OAuth2 token for Microsoft Graph API using client credentials flow.
    """
    logger.info("Requesting Graph API token")
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
            token = response.json()["access_token"]
            logger.debug("Successfully obtained Graph API token")
            return token
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to get Graph API token: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to authenticate with Graph API: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error getting Graph API token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to authenticate with Graph API: {str(e)}")


@router.post("/mail/send")
async def send_mail(mail_request: MailRequest, api_key: str = Depends(get_verify_api_key())):
    """
    Send an email via Microsoft Graph API.
    
    Parameters:
    - sender: Email address to send from (must have SendAs permissions)
    - subject: Email subject line
    - body: HTML body content
    - to: Comma-separated email addresses for To recipients
    - cc: Optional comma-separated email addresses for Cc recipients
    """
    logger.info(f"Sending email from {mail_request.sender} to {mail_request.to}")
    
    try:
        # Get Graph API token
        token = await get_graph_token()
        
        # Parse recipients
        to_recipients = [{"emailAddress": {"address": addr.strip()}} for addr in mail_request.to.split(",") if addr.strip()]
        cc_recipients = []
        if mail_request.cc:
            cc_recipients = [{"emailAddress": {"address": addr.strip()}} for addr in mail_request.cc.split(",") if addr.strip()]
        
        # Construct mail message
        message = {
            "message": {
                "subject": mail_request.subject,
                "body": {
                    "contentType": "HTML",
                    "content": mail_request.body
                },
                "toRecipients": to_recipients,
                "ccRecipients": cc_recipients
            },
            "saveToSentItems": "true"
        }
        
        # Send mail using Graph API
        url = f"https://graph.microsoft.com/v1.0/users/{mail_request.sender}/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=message, headers=headers)
            response.raise_for_status()
        
        logger.info(f"Successfully sent email from {mail_request.sender} to {mail_request.to}")
        return {
            "message": "Email sent successfully",
            "sender": mail_request.sender,
            "to": mail_request.to,
            "cc": mail_request.cc,
            "subject": mail_request.subject
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to send email: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.get("/mail/receive")
async def receive_mail(api_key: str = Depends(get_verify_api_key())):
    """
    Fetch emails from shared mailbox (idea@angermeier.net), create ideas in ChromaDB,
    enhance with AI-generated tags, and move processed emails to Archive folder.
    """
    logger.info(f"Fetching emails from shared mailbox: {SHARED_MAILBOX}")
    
    # Import here to avoid circular dependencies
    from api.main import ideas, embed_text
    import json
    import uuid
    import html
    import re
    
    try:
        # Get Graph API token
        token = await get_graph_token()
        
        # Fetch messages from shared mailbox inbox
        url = f"https://graph.microsoft.com/v1.0/users/{SHARED_MAILBOX}/mailFolders/inbox/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        messages = data.get("value", [])
        logger.info(f"Found {len(messages)} messages in inbox")
        
        processed_ideas = []
        
        for message in messages:
            message_id = message["id"]
            subject = message.get("subject", "No Subject")
            body_content = message.get("body", {}).get("content", "")
            
            logger.info(f"Processing message: {subject} (ID: {message_id})")
            
            # Extract text from HTML body
            # Simple HTML stripping - remove tags but keep content
            body_text = re.sub(r'<[^>]+>', '', body_content)
            body_text = html.unescape(body_text).strip()
            
            if not body_text:
                logger.warning(f"Message {message_id} has empty body, skipping")
                continue
            
            try:
                # Generate tags using AI (similar to enhance endpoint)
                logger.debug(f"Calling OpenAI API to generate tags for idea from email")
                ai_headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
                if OPENAI_ORG_ID:
                    ai_headers["OpenAI-Organization"] = OPENAI_ORG_ID
                
                # Create prompt for OpenAI
                prompt = f"""Du bist ein präziser deutscher Lektor.

Given the following idea title and description from an email, please generate exactly 5 relevant tags that describe the core themes of this idea.

Title: {subject}

Description:
{body_text}

Please respond ONLY with a JSON object in this exact format (no markdown, no code blocks):
{{"tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}}"""
                
                async with httpx.AsyncClient(timeout=60) as client_http:
                    ai_response = await client_http.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=ai_headers,
                        json={
                            "model": "gpt-4o-mini",
                            "messages": [
                                {"role": "system", "content": "You are a helpful assistant that generates tags. Always respond with valid JSON only."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 500
                        }
                    )
                ai_response.raise_for_status()
                ai_data = ai_response.json()
                
                # Extract tags from AI response
                content = ai_data["choices"][0]["message"]["content"].strip()
                logger.debug(f"OpenAI response: {content}")
                
                # Parse JSON response (remove markdown code blocks if present)
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                
                result = json.loads(content)
                tags = result["tags"][:5]  # Ensure max 5 tags
                
                logger.info(f"Generated {len(tags)} tags for email: {tags}")
                
                # Create idea in ChromaDB
                idea_id = str(uuid.uuid4())
                doc = f"{subject}\n\n{body_text}\n\nTags: {', '.join(tags)}"
                vec = await embed_text(doc)
                
                metadata = {
                    "title": subject,
                    "tags": ",".join(tags),
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "New"
                }
                
                ideas.add(ids=[idea_id], documents=[doc], embeddings=[vec], metadatas=[metadata])
                logger.info(f"Successfully created idea {idea_id} from email")
                
                processed_ideas.append({
                    "id": idea_id,
                    "title": subject,
                    "tags": tags,
                    "email_id": message_id
                })
                
                # Move email to Archive folder
                # First, get the Archive folder ID
                archive_url = f"https://graph.microsoft.com/v1.0/users/{SHARED_MAILBOX}/mailFolders"
                async with httpx.AsyncClient(timeout=30) as client:
                    folders_response = await client.get(archive_url, headers=headers)
                    folders_response.raise_for_status()
                    folders = folders_response.json().get("value", [])
                
                archive_folder_id = None
                for folder in folders:
                    if folder.get("displayName", "").lower() == "archive":
                        archive_folder_id = folder["id"]
                        break
                
                if archive_folder_id:
                    # Move message to Archive
                    move_url = f"https://graph.microsoft.com/v1.0/users/{SHARED_MAILBOX}/messages/{message_id}/move"
                    move_data = {"destinationId": archive_folder_id}
                    
                    async with httpx.AsyncClient(timeout=30) as client:
                        move_response = await client.post(move_url, json=move_data, headers=headers)
                        move_response.raise_for_status()
                    
                    logger.info(f"Moved email {message_id} to Archive folder")
                else:
                    logger.warning(f"Archive folder not found, email {message_id} remains in inbox")
                    
            except Exception as e:
                logger.error(f"Failed to process email {message_id}: {e}", exc_info=True)
                # Continue processing other emails even if one fails
                continue
        
        logger.info(f"Successfully processed {len(processed_ideas)} emails into ideas")
        return {
            "message": f"Processed {len(processed_ideas)} emails",
            "ideas_created": processed_ideas
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch emails: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error receiving emails: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to receive emails: {str(e)}")
