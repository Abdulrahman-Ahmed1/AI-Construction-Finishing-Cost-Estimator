from __future__ import annotations

import streamlit as st

from chatbot.i18n import LANGUAGES, t
from chatbot.parser import parse_answer
from cost_engine.engine import build_detailed_estimate
from src.prediction.predict import InvalidInputError, predict_finishing_cost


st.set_page_config(
    page_title="Smart Finishing AI",
    page_icon="🏠",
    layout="wide"
)


QUESTIONS = [
    ("Apartment_Area_m2", "area", "number"),
    ("Rooms", "rooms", "int"),
    ("Bathrooms", "bathrooms", "int"),
    ("Master_Bathrooms", "master_bathrooms", "int"),
    ("Balconies", "balconies", "int"),
    ("Receptions", "receptions", "int"),
    ("Finishing_Level", "level", "quality"),
    ("Ceilings_Quality", "ceilings", "quality"),
    ("Doors_Quality", "doors", "quality"),
    ("Electrical_Basic_Quality", "electrical_basic", "quality"),
    ("Electrical_Finishing_Quality", "electrical_finishing", "quality"),
    ("Flooring_Quality", "flooring", "quality"),
    ("Paints_Quality", "paints", "quality"),
    ("Plumbing_Quality", "plumbing_quality", "quality"),
    ("Sanitary_Quality", "sanitary", "quality"),
    ("Include_Reception_Ceiling_Upgrade", "ceiling_upgrade", "yesno"),
    ("Include_Reception_Chandelier", "chandelier", "yesno"),
    ("Include_Master_Bathroom_Upgrade", "master_upgrade", "yesno"),
    ("Plumbing_System", "plumbing_system", "plumbing"),
]


def reset_chat():
    st.session_state.messages = []
    st.session_state.answers = {}
    st.session_state.q_index = 0
    st.session_state.result = None


CATEGORY_TRANSLATIONS = {
    "Ceilings": "الأسقف",
    "Ceiling": "الأسقف",
    "Doors": "الأبواب",
    "Door": "الأبواب",
    "Electrical Basic": "الكهرباء الأساسية",
    "Basic Electrical": "الكهرباء الأساسية",
    "Electrical Finishing": "الكهرباء النهائية",
    "Finishing Electrical": "الكهرباء النهائية",
    "Flooring": "الأرضيات",
    "Floors": "الأرضيات",
    "Paints": "الدهانات",
    "Paint": "الدهانات",
    "Plumbing": "السباكة",
    "Sanitary": "الأدوات الصحية",
    "Sanitary Ware": "الأدوات الصحية",
    "Reception Ceiling": "سقف الريسبشن",
    "Reception Chandelier": "نجفة الريسبشن",
    "Master Bathroom": "حمام الماستر",
    "Master Bathroom Upgrade": "تطوير حمام الماستر",
}


UNIT_TRANSLATIONS = {
    "piece": "قطعة",
    "pieces": "قطع",
    "unit": "وحدة",
    "units": "وحدات",
    "m2": "م²",
    "m²": "م²",
    "meter": "متر",
    "meters": "متر",
    "liter": "لتر",
    "liters": "لتر",
    "box": "علبة",
    "boxes": "علب",
    "set": "طقم",
    "sets": "أطقم",
}


def translate_category(category, language):
    if language == "ar":
        return CATEGORY_TRANSLATIONS.get(
            category,
            category
        )

    return category


def translate_unit(unit, language):
    if language == "ar":
        return UNIT_TRANSLATIONS.get(
            str(unit).lower(),
            unit
        )

    return unit


if "language" not in st.session_state:
    st.session_state.language = None


if "messages" not in st.session_state:
    reset_chat()


if st.session_state.language is None:

    st.title("🏠 Smart Finishing AI")

    st.markdown("## Choose your language")

    st.write(
        "Please select your preferred language before starting the assistant."
    )

    language_name = st.radio(
        "Language / اللغة",
        list(LANGUAGES.keys()),
        horizontal=True
    )

    if st.button(
        "Continue",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.language = LANGUAGES[
            language_name
        ]

        reset_chat()

        st.rerun()

    st.stop()


language = st.session_state.language


current_language_name = next(
    name
    for name, value in LANGUAGES.items()
    if value == language
)


st.sidebar.title("⚙️ Settings")


if language == "ar":

    st.sidebar.write(
        f"**اللغة:** {current_language_name}"
    )

    change_language_text = "تغيير اللغة"

else:

    st.sidebar.write(
        f"**Language:** {current_language_name}"
    )

    change_language_text = "Change Language"


if st.sidebar.button(
    change_language_text,
    use_container_width=True
):

    st.session_state.language = None

    reset_chat()

    st.rerun()


if st.sidebar.button(
    t("restart", language),
    use_container_width=True
):

    reset_chat()

    st.rerun()


st.title("🏠 Smart Finishing AI")

st.caption(
    t("welcome", language)
)


if not st.session_state.messages:

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": t(
                "welcome",
                language
            )
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": t(
                QUESTIONS[0][1],
                language
            )
        }
    )


for msg in st.session_state.messages:

    with st.chat_message(
        msg["role"]
    ):

        st.write(
            msg["content"]
        )


if (
    st.session_state.result is None
    and st.session_state.q_index < len(QUESTIONS)
):

    if language == "en":

        chat_placeholder = "Type your answer..."

    else:

        chat_placeholder = "اكتب إجابتك..."


    prompt = st.chat_input(
        chat_placeholder
    )


    if prompt:

        key, qkey, kind = QUESTIONS[
            st.session_state.q_index
        ]


        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )


        try:

            value = parse_answer(
                prompt,
                kind
            )


            st.session_state.answers[
                key
            ] = value


            if (
                key == "Master_Bathrooms"
                and value
                > st.session_state.answers.get(
                    "Bathrooms",
                    0
                )
            ):

                if language == "en":

                    error_message = (
                        "Master bathrooms cannot exceed "
                        "total bathrooms."
                    )

                else:

                    error_message = (
                        "عدد حمامات الماستر لا يمكن أن "
                        "يتجاوز إجمالي عدد الحمامات."
                    )

                raise ValueError(
                    error_message
                )


            if (
                key == "Bathrooms"
                and value
                < st.session_state.answers.get(
                    "Master_Bathrooms",
                    0
                )
            ):

                if language == "en":

                    error_message = (
                        "Total bathrooms cannot be less "
                        "than master bathrooms."
                    )

                else:

                    error_message = (
                        "إجمالي عدد الحمامات لا يمكن أن "
                        "يكون أقل من عدد حمامات الماستر."
                    )

                raise ValueError(
                    error_message
                )


            st.session_state.q_index += 1


            if (
                st.session_state.q_index
                < len(QUESTIONS)
            ):

                next_key = QUESTIONS[
                    st.session_state.q_index
                ][1]


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": t(
                            next_key,
                            language
                        )
                    }
                )


            else:

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": t(
                            "thinking",
                            language
                        )
                    }
                )


                try:

                    result = predict_finishing_cost(
                        st.session_state.answers
                    )


                    details = build_detailed_estimate(
                        st.session_state.answers,
                        result[
                            "estimated_total_cost_egp"
                        ]
                    )


                    result["details"] = details


                    st.session_state.result = result


                except (
                    InvalidInputError,
                    FileNotFoundError,
                    ValueError
                ) as exc:

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": str(exc)
                        }
                    )


        except ValueError as exc:

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        f"{t('error', language)}\n\n"
                        f"{exc}"
                    )
                }
            )


        st.rerun()


if st.session_state.result:

    result = st.session_state.result


    total = result[
        "estimated_total_cost_egp"
    ]


    low = result[
        "prediction_range"
    ]["low_egp"]


    high = result[
        "prediction_range"
    ]["high_egp"]


    st.divider()


    st.subheader(
        f"💰 {t('total', language)}"
    )


    if language == "ar":

        st.metric(
            "جنيه مصري",
            f"{total:,.0f}"
        )

    else:

        st.metric(
            "EGP",
            f"{total:,.0f}"
        )


    if language == "ar":

        st.caption(
            f"{t('range', language)}: "
            f"{low:,.0f} – {high:,.0f} جنيه مصري"
        )

    else:

        st.caption(
            f"{t('range', language)}: "
            f"{low:,.0f} – {high:,.0f} EGP"
        )


    st.subheader(
        f"📊 {t('breakdown', language)}"
    )


    categories = result[
        "details"
    ]["categories"]


    cols = st.columns(2)


    for i, (
        category,
        cost
    ) in enumerate(
        categories.items()
    ):

        display_category = translate_category(
            category,
            language
        )


        if language == "ar":

            cols[i % 2].metric(
                display_category,
                f"{cost:,.0f} جنيه"
            )

        else:

            cols[i % 2].metric(
                display_category,
                f"{cost:,.0f} EGP"
            )


    st.subheader(
        f"🧾 {t('included', language)}"
    )


    by_category = {}


    for line in result[
        "details"
    ]["lines"]:

        by_category.setdefault(
            line["category"],
            []
        ).append(line)


    for category, lines in by_category.items():

        display_category = translate_category(
            category,
            language
        )


        category_cost = categories.get(
            category,
            0
        )


        if language == "ar":

            expander_title = (
                f"{display_category} — "
                f"{category_cost:,.0f} جنيه"
            )

        else:

            expander_title = (
                f"{display_category} — "
                f"{category_cost:,.0f} EGP"
            )


        with st.expander(
            expander_title
        ):

            for line in lines:

                product_name = line[
                    "product_name"
                ]

                quantity = line[
                    "quantity"
                ]

                unit = translate_unit(
                    line["unit"],
                    language
                )

                unit_price = line[
                    "unit_price_egp"
                ]

                estimated_cost = line[
                    "estimated_cost_egp"
                ]

                brand = line[
                    "brand"
                ]


                if language == "ar":

                    text = (
                        f"**{product_name}** — "
                        f"{quantity:,.2f} "
                        f"{unit} × "
                        f"{unit_price:,.2f} جنيه "
                        f"≈ **{estimated_cost:,.2f} جنيه**"
                    )

                else:

                    text = (
                        f"**{product_name}** — "
                        f"{quantity:,.2f} "
                        f"{unit} × "
                        f"{unit_price:,.2f} EGP "
                        f"≈ **{estimated_cost:,.2f} EGP**"
                    )


                if brand:

                    text += (
                        f" · {brand}"
                    )


                st.write(
                    text
                )


    allocation_method = result[
        "details"
    ]["allocation_method"]


    if language == "ar":

        st.info(
            "تم توزيع التكلفة التقديرية "
            "بناءً على بيانات أسعار المنتجات "
            "وبيانات التدريب المستخدمة في النموذج."
        )

    else:

        st.info(
            allocation_method
        )


    st.warning(
        t(
            "disclaimer",
            language
        )
    )
