"""Dependency injection — يجمع كل التبعيات في مكان واحد."""
from fastapi import Depends, Request

from app.infra.ocr.pipeline import InferencePipeline
from app.domain.identity.service import EnrollmentService
from app.domain.identity.store import IdentityStore
from app.infra.db.repositories import SQLIdentityStore
from app.infra.external.ministry_client import MinistryClient


def get_pipeline(request: Request) -> InferencePipeline:
    return request.app.state.pipeline


def get_issuer(request: Request):
    return request.app.state.issuer


def get_identity_store() -> IdentityStore:
    return SQLIdentityStore()


def get_ministry_client() -> MinistryClient:
    return MinistryClient()


def get_enrollment_service(
    store: IdentityStore = Depends(get_identity_store),
    ministry: MinistryClient = Depends(get_ministry_client),
    issuer = Depends(get_issuer),
) -> EnrollmentService:
    return EnrollmentService(store=store, ministry=ministry, issuer=issuer)