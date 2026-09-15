from datetime import datetime, timedelta, timezone
from typing import Any
from sd_jwt.issuer import SDJWTIssuer
from sd_jwt.common import SDObj


class SDJWTIdentityIssuer:
    """
    مُصدر SD-JWT VC للهوية الجزائرية.
    - الحقول الحساسة (NIN, date_of_birth) قابلة للإفصاح الانتقائي.
    - التوقيع باستخدام Ed25519 (أو ES256).
    """

    VC_TYPE = "AlgerianNationalIDCredential"
    VCT = "https://id.gov.dz/credentials/national-id/v1"

    def __init__(self, private_key, issuer_id: str = "https://id.gov.dz"):
        self.private_key = private_key
        self.issuer_id = issuer_id

    def build_payload(self, identity) -> dict[str, Any]:
        return {
            "iss": self.issuer_id,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int(
                (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
            ),
            "vct": self.VCT,
            # الحقول غير الحساسة (ظاهرة دائمًا)
            "given_name": identity.person.first_name_fr,
            "family_name": identity.person.last_name_fr,
            "nationality": "DZ",
            # الحقول الحساسة (selective disclosure)
            "nin": SDObj(identity.nin),
            "date_of_birth": SDObj(identity.person.date_of_birth.isoformat()),
            "place_of_birth": SDObj(identity.person.place_of_birth),
            "verification_level": identity.verification_level.value,
        }

    def issue(self, identity) -> str:
        payload = self.build_payload(identity)
        sdjwt = SDJWTIssuer(
            payload=payload,
            issuer_keypair=(self.private_key, None),
            sign_alg="EdDSA",
            add_decoy_claims=True,        # حماية ضد التنبؤ
            serialization_format="compact",
        )
        return sdjwt.sd_jwt_issuance