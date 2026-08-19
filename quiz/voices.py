VOICE_MODELS = {
    "MAN": {
        "en_US-ryan-medium": "Ryan — American Male",
        "en_US-hfc_male-medium": "HFC Male — American Male",
    },
    "WOMAN": {
        "en_US-amy-medium": "Amy — American Female",
        "en_US-hfc_female-medium": "HFC Female — American Female",
    },
}

DEFAULT_VOICE_MODELS = {
    "MAN": "en_US-ryan-medium",
    "WOMAN": "en_US-amy-medium",
}


def voice_choices(actor):
    return tuple(VOICE_MODELS[actor].items())
