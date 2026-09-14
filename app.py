from __future__ import annotations

import streamlit as st

from chatbot.i18n import (
    LANGUAGES,
    t,
    translate_category,
    translate_unit,
)

from chatbot.parser import parse_answer

from cost_engine.engine import (
    build_detailed_estimate
)

from src.prediction.predict import (
    InvalidInputError,
    predict_finishing_cost
)


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
    (
        "Electrical_Basic_Quality",
        "electrical_basic",
        "quality"
    ),
    (
        "Electrical_Finishing_Quality",
        "electrical_finishing",
        "quality"
    ),
    ("Flooring_Quality", "flooring", "quality"),
    ("Paints_Quality", "paints", "quality"),
    ("Plumbing_Quality", "plumbing_quality", "quality"),
    ("Sanitary_Quality", "sanitary", "quality"),
    (
        "Include_Reception_Ceiling_Upgrade",
        "ceiling_upgrade",
        "yesno"
    ),
    (
        "Include_Reception_Chandelier",
        "chandelier",
        "yesno"
    ),
    (
        "Include_Master_Bathroom_Upgrade",
        "master_upgrade",
        "yesno"
    ),
    ("Plumbing_System", "plumbing_system", "plumbing"),
]


def reset_chat():

    st.session_state.messages = []

    st.session_state.answers = {}

    st.session_state.q_index = 0

    st.session_state.result = None


if "language" not in st.session_state:

    st.session_state.language = None


if "messages" not in st.session_state:

    reset_chat()


if st.session_state.language is None:

    st.title(
        "🏠 Smart Finishing AI"
    )

    st.markdown(
        "## Choose your language"
    )

    st.write(
        "Please select your preferred language "
        "before starting the assistant."
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

        st.session_state.language = (
            LANGUAGES[language_name]
        )

        reset_chat()

        st.rerun()

    st.stop()


language = st.session_state.language


current_language_name = next(
    name
    for name, value in LANGUAGES.items()
    if value == language
)


st.sidebar.title(
    f"⚙️ {t('settings', language)}"
)


st.sidebar.write(
    f"**{t('language', language)}:** "
    f"{current_language_name}"
)


if st.sidebar.button(
    t("change_language", language),
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


st.title(
    "🏠 Smart Finishing AI"
)


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
    and st.session_state.q_index
    < len(QUESTIONS)
):

    prompt = st.chat_input(
        t(
            "type_answer",
            language
        )
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

                raise ValueError(
                    t(
                        "master_bathrooms_error",
                        language
                    )
                )


            if (
                key == "Bathrooms"
                and value
                < st.session_state.answers.get(
                    "Master_Bathrooms",
                    0
                )
            ):

                raise ValueError(
                    t(
                        "bathrooms_error",
                        language
                    )
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


                    details = (
                        build_detailed_estimate(
                            st.session_state.answers,
                            result[
                                "estimated_total_cost_egp"
                            ]
                        )
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


    st.metric(
        t("currency_name", language),
        f"{total:,.0f}"
    )


    st.caption(
        f"{t('range', language)}: "
        f"{low:,.0f} – "
        f"{high:,.0f} "
        f"{t('currency_name', language)}"
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

        display_category = (
            translate_category(
                category,
                language
            )
        )


        cols[i % 2].metric(
            display_category,
            (
                f"{cost:,.0f} "
                f"{t('currency_name', language)}"
            )
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

        display_category = (
            translate_category(
                category,
                language
            )
        )


        category_cost = categories.get(
            category,
            0
        )


        with st.expander(
            (
                f"{display_category} — "
                f"{category_cost:,.0f} "
                f"{t('currency_name', language)}"
            )
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


                text = (
                    f"**{product_name}** — "
                    f"{quantity:,.2f} "
                    f"{unit} × "
                    f"{unit_price:,.2f} "
                    f"{t('currency_name', language)} "
                    f"≈ **{estimated_cost:,.2f} "
                    f"{t('currency_name', language)}**"
                )


                if brand:

                    text += (
                        f" · {brand}"
                    )


                st.write(
                    text
                )


    st.info(
        t(
            "allocation_method",
            language
        )
    )


    st.warning(
        t(
            "disclaimer",
            language
        )
    )
