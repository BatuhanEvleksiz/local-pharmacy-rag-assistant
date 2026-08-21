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
                "Bu bir acil saglik durumu olabilir. Bu uygulama acil durum yonetimi "
                "yapamaz; hemen 112'yi arayin veya en yakin saglik kurulusuna basvurun. "
                "Ilac/zehirlenme suphelerinde doktor, eczaci veya yetkili zehir danisma "
                "hatti ile gorusun."
            ),
        )

    if any(term in normalized for term in DOSE_CHANGE_TERMS):
        return SafetyDecision(
            allowed=False,
            category="dose_change",
            message=(
                "Bu soru doz degisikligi veya ilaci birakma karari gerektiriyor. "
                "Bu uygulama doz tavsiyesi vermez; doktorunuza ya da eczaciniza "
                "danismadan doz degistirmeyin."
            ),
        )

    if any(term in normalized for term in ADVICE_TERMS):
        return SafetyDecision(
            allowed=False,
            category="medical_advice",
            message=(
                "Bu soru kisisel tibbi karar veya tedavi tavsiyesi gerektiriyor. "
                "Ben yalnizca yuklenen belgelerdeki bilgileri ozetleyebilirim; ilaci "
                "kullanma, birakma veya doz degistirme karari icin doktorunuza ya da "
                "eczaciniza danisin."
            ),
        )

    return SafetyDecision(allowed=True, category="information")


def safety_footer() -> str:
    return (
        "\n\nNot: Bu yanit yalnizca yuklenen belge metinlerine dayali bilgi amaclidir; "
        "doktor veya eczaci danismanliginin yerine gecmez."
    )
