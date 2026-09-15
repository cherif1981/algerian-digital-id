from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/oid4vci", tags=["OpenID4VCI"])


class CredentialOffer(BaseModel):
    credential_issuer: str
    credential_configuration_ids: list[str]
    grants: dict


@router.get("/.well-known/openid-credential-issuer")
async def credential_issuer_metadata():
    """
    OpenID4VCI §4.2 — Credential Issuer Metadata.
    يكتشف العميل (Wallet) قدرات المُصدر.
    """
    return {
        "credential_issuer": "https://id.gov.dz",
        "credential_endpoint": "https://id.gov.dz/oid4vci/credential",
        "token_endpoint": "https://id.gov.dz/oid4vci/token",
        "credential_configurations_supported": {
            "national_id_sd_jwt": {
                "format": "vc+sd-jwt",
                "vct": "https://id.gov.dz/credentials/national-id/v1",
                "cryptographic_binding_methods_supported": ["jwk"],
                "credential_signing_alg_values_supported": ["EdDSA", "ES256"],
                "proof_types_supported": {
                    "jwt": {
                        "proof_signing_alg_values_supported": ["ES256"]
                    }
                },
                "claims": {
                    "given_name": {"display": [{"name": "الاسم", "locale": "ar"}]},
                    "family_name": {"display": [{"name": "اللقب", "locale": "ar"}]},
                    "nin": {"display": [{"name": "رقم التعريف الوطني", "locale": "ar"}]},
                },
            }
        },
    }


@router.post("/credential")
async def issue_credential(proof: dict):
    """
    OpenID4VCI §6 — Credential Endpoint.
    - يتحقق من proof (Key Binding)
    - يصدر SD-JWT VC
    - يعيد c_nonce جديد
    """
    # TODO: التحقق من proof JWT + c_nonce
    # TODO: التحقق من صلاحية المستخدم (access token)
    # TODO: استدعاء SDJWTIdentityIssuer.issue()
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/token")
async def token_endpoint(grant_type: str, pre_authorized_code: str | None = None):
    """
    OpenID4VCI §5 — Token Endpoint.
    يدعم: pre-authorized_code, authorization_code.
    """
    # TODO: تنفيذ تدفق pre-authorized_code (الأكثر ملاءمة للإصدار الحكومي)
    raise HTTPException(status_code=501, detail="Not implemented yet")