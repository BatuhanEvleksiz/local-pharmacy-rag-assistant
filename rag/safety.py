from __future__ import annotations

from dataclasses import dataclass


EMERGENCY_TERMS = [
    "cok fazla",
    "çok fazla",
    "fazla ic",
    "fazla iç",
    "fazla ilac",
    "fazla ilaç",
    "asiri doz",
    "aşırı doz",
    "zehirl",
    "nefes alam",
    "nefes almakta zorlan",
    "nefes darligi",
    "nefes darlığı",
    "bayildi",
    "bayıldı",
    "suur",
    "şuur",
    "anafilaksi",
    "intihar",
]

ADVICE_TERMS = [
    "kullanayim mi",
    "kullanayım mı",
    "alabilir miyim",
    "iyi gelir mi",
    "tedavi oner",
    "tedavi öner",
    "recete",
    "reçete",
    "tani koy",
    "tanı koy",
]

DOSE_CHANGE_TERMS = [
    "dozu artir",
    "dozu artır",
    "artirabilir miyim",
    "artırabilir miyim",
    "iki kat",
    "katina",
    "katına",
    "dozu azalt",
    "birakabilir miyim",
    "bırakabilir miyim",
]


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    category: str
    message: str | None = None


def classify_question(question: str) -> SafetyDecision:
    normalized = question.lower()
    if any(term in normalized for term in EMERGENCY_TERMS):
        return SafetyDecision(
            allowed=False,
            category="emergency",
            message=(
                "Bu bir acil sağlık durumu olabilir. Bu uygulama acil durum yönetimi "
                "yapamaz; hemen 112'yi arayın veya en yakın sağlık kuruluşuna başvurun. "
                "İlaç/zehirlenme şüphelerinde doktor, eczacı veya yetkili zehir danışma "
                "hattı ile görüşün."
            ),
        )

    if any(term in normalized for term in DOSE_CHANGE_TERMS):
        return SafetyDecision(
            allowed=False,
            category="dose_change",
            message=(
                "Bu soru doz değişikliği veya ilacı bırakma kararı gerektiriyor. "
                "Bu uygulama doz tavsiyesi vermez; doktorunuza ya da eczacınıza "
                "danışmadan doz değiştirmeyin."
            ),
        )

    if any(term in normalized for term in ADVICE_TERMS):
        return SafetyDecision(
            allowed=False,
            category="medical_advice",
            message=(
                "Bu soru kişisel tıbbi karar veya tedavi tavsiyesi gerektiriyor. "
                "Ben yalnızca yüklenen belgelerdeki bilgileri özetleyebilirim; ilacı "
                "kullanma, bırakma veya doz değiştirme kararı için doktorunuza ya da "
                "eczacınıza danışın."
            ),
        )

    return SafetyDecision(allowed=True, category="information")


def safety_footer() -> str:
    return (
        "\n\nNot: Bu yanıt yalnızca yüklenen belge metinlerine dayalı bilgi amaçlıdır; "
        "doktor veya eczacı danışmanlığının yerine geçmez."
    )
