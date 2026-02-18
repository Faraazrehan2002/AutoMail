"""
Email templates CRUD endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import re

from ..db import get_db
from ..models import Template, User
from ..dependencies import get_current_user

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    name: str
    subject: str
    html_body: str
    variables: Optional[List[str]] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_body: Optional[str] = None
    variables: Optional[List[str]] = None


class TemplateResponse(BaseModel):
    id: str
    user_id: str
    name: str
    subject: str
    html_body: str
    variables: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


def extract_variables(html_body: str) -> List[str]:
    """Extract variable names from template ({{variable_name}})"""
    pattern = r'\{\{(\w+)\}\}'
    matches = re.findall(pattern, html_body)
    return list(set(matches))  # Remove duplicates


def render_template(html_body: str, subject: str, variables: dict) -> tuple[str, str]:
    """Render template with variables"""
    rendered_body = html_body
    rendered_subject = subject
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        rendered_body = rendered_body.replace(placeholder, str(value))
        rendered_subject = rendered_subject.replace(placeholder, str(value))
    
    return rendered_subject, rendered_body


@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all templates for the current user"""
    templates = db.query(Template).filter(Template.user_id == current_user.id).order_by(Template.created_at.desc()).all()
    return templates


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new email template"""
    # Extract variables if not provided
    variables = template_data.variables
    if variables is None:
        variables = extract_variables(template_data.html_body)
        # Also check subject
        subject_vars = extract_variables(template_data.subject)
        variables = list(set(variables + subject_vars))
    
    template = Template(
        user_id=current_user.id,
        name=template_data.name,
        subject=template_data.subject,
        html_body=template_data.html_body,
        variables=variables
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    if template_data.name is not None:
        template.name = template_data.name
    if template_data.subject is not None:
        template.subject = template_data.subject
    if template_data.html_body is not None:
        template.html_body = template_data.html_body
        # Re-extract variables if body changed
        if template_data.variables is None:
            variables = extract_variables(template.html_body)
            subject_vars = extract_variables(template.subject)
            template.variables = list(set(variables + subject_vars))
    if template_data.variables is not None:
        template.variables = template_data.variables
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return None
