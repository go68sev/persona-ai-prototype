PREFERENCE_PARAMETERS = {

# -------------------------------------------------------------
# SECTION 1 — PERSONAL BACKGROUND
# -------------------------------------------------------------

    "1": {  # What are you studying?
        "target": "academic_program",
        "type": "text",
        "logic": "store_raw",
        "default": "not-provided"
    },

    "2": {  # Which subjects are you taking?
        "target": "current_courses",
        "type": "list",
        "logic": "split_by_comma_or_newline",
        "default": []
    },

    "3": {  # Semester number
        "target": "semester",
        "type": "number",
        "logic": "extract_integer",
        "default": None
    },

    "4": {  # Academic goals
        "target": "academic_goals",
        "type": "text",
        "logic": "store_raw",
        "default": "none-provided"
    },

    "5": {  # Favorite subjects
        "target": "favorite_subjects",
        "type": "text",
        "logic": "store_raw",
        "default": []
    },

    "6": {  # Age
        "target": "age",
        "type": "number",
        "logic": "extract_integer",
        "default": None
    }, 

    # -------------------------------------------------------------
    # SECTION 2 — LEARNING PREFERENCES
    # -------------------------------------------------------------

    "7": {
        "target": "examples_vs_theory",
        "type": "mcq",
        "mapping": {
            "Examples first": "examples-first",
            "Theory first": "theory-first",
            "A mix of both": "mixed",
        },
        "default": "mixed"
    },

    "8": {
        "target": "visual_vs_verbal",
        "type": "mcq",
        "mapping": {
            "Diagrams/visuals": "visual",
            "Text-based explanations": "verbal",
            "Both": "mixed",
        },
        "default": "mixed"
    },

    "9": {
        "target": "uses_analogies",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "Sometimes": "sometimes",
            "No": False,
        },
        "default": False
    },

    "10": {
        "target": "explanation_preference",
        "type": "mcq",
        "mapping": {
            "Step-by-step": "step-by-step",
            "High-level overview": "high-level",
            "Both depending on topic": "mixed",
        },
        "default": "mixed"
    },

    "11": {
        "target": "guidance_preference",
        "type": "mcq",
        "mapping": {
            "Clear structure and guidance": "structured",
            "Independent exploration": "independent",
            "A balance of both": "balanced",
        },
        "default": "balanced"
    },

    "12": {
        "target": "learning_mode",
        "type": "mcq",
        "mapping": {
            "Repetition and practice": "practice",
            "Understanding deep concepts": "conceptual",
        },
        "default": "practice"
    },

    "13": {
        "target": "memorization_strategy",
        "type": "mcq",
        "mapping": {
            "Flashcards": "flashcards",
            "Summaries": "summaries",
            "Mnemonics": "mnemonics",
            "Other": "other",
        },
        "default": "summaries"
    },

    "14": {
        "target": "study_rhythm",
        "type": "mcq",
        "mapping": {
            "Regular throughout the semester": "regular",
            "Mostly near exams": "cram",
            "Mixed": "mixed",
        },
        "default": "mixed"
    },

    "15": {
        "target": "detail_level",
        "type": "rating",
        "scale": 10,
        "default": 5
    },

    "16": {
        "target": "mistake_handling",
        "type": "mcq",
        "mapping": {
            "Fix it immediately": "immediate-fix",
            "Move on and revisit later": "deferred",
        },
        "default": "immediate-fix"
    },

    "17": {
        "target": "review_style",
        "type": "mcq",
        "mapping": {
            "Spread across several days": "spaced",
            "One or two long sessions": "intensive",
            "Depends": "depends",
        },
        "default": "depends"
    },

    "18": {
        "target": "flashcard_preference",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "Sometimes": "sometimes",
            "No": False,
        },
        "default": False
    }, 

    # -------------------------------------------------------------
    # SECTION 3 — CONTENT PREFERENCES
    # -------------------------------------------------------------

    "19": {
        "target": "video_learning",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "Sometimes": "sometimes",
            "No": False,
        },
        "default": "sometimes"
    },

    "20": {
        "target": "code_examples",
        "type": "mcq",
        "mapping": {
            "Yes": "yes",
            "Only if necessary": "if-necessary",
            "No": "no",
        },
        "default": "if-necessary"
    },

    "21": {
        "target": "example_quantity",
        "type": "mcq",
        "mapping": {
            "Multiple examples": "multiple",
            "One strong example": "single",
        },
        "default": "single"
    },

    "22": {
        "target": "practice_problems",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "Maybe later": "later",
            "No": False,
        },
        "default": True
    },

    "23": {
        "target": "input_modality",
        "type": "mcq",
        "mapping": {
            "Reading text": "reading",
            "Listening to audio": "audio",
            "Both equally": "mixed",
        },
        "default": "mixed"
    },

    "24": {
        "target": "summary_preference",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "Sometimes": "sometimes",
            "No": False,
        },
        "default": True
    },

    "25": {
        "target": "diagram_preference",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "Sometimes": "sometimes",
            "No": False,
        },
        "default": True
    },

        # -------------------------------------------------------------
    # SECTION 4 — COMPARISON QUESTIONS (A vs B)
    # -------------------------------------------------------------

    "26": {
        "target": "response_depth",
        "type": "mcq",
        "mapping": {
            "Quick response": "quick",
            "Deep explanation": "deep",
        },
        "default": "deep"
    },

    "27": {
        "target": "question_engagement",
        "type": "mcq",
        "mapping": {
            "Yes": True,
            "No, just answer directly": False,
        },
        "default": True
    },

    "28": {
        "target": "writing_style",
        "type": "mcq",
        "mapping": {
            "Formal academic": "formal",
            "Conversational": "conversational",
        },
        "default": "conversational"
    },

    "29": {
        "target": "study_focus",
        "type": "mcq",
        "mapping": {
            "Exploring side topics": "exploratory",
            "Staying focused on the main goal": "focused",
        },
        "default": "focused"
    },

    "30": {
        "target": "explanation_style",
        "type": "mcq",
        "mapping": {
            "A": "simple",
            "B": "technical",
        },
        "default": "technical"
    },

    "31": {
        "target": "format_preference",
        "type": "mcq",
        "mapping": {
            "A": "visual",
            "B": "verbal",
        },
        "default": "visual"
    },

    "32": {
        "target": "learning_approach",
        "type": "mcq",
        "mapping": {
            "A": "active",
            "B": "reflective",
        },
        "default": "active"
    },

    "33": {
        "target": "feedback_style",
        "type": "mcq",
        "mapping": {
            "A": "supportive",
            "B": "direct",
        },
        "default": "supportive"
    },

    "34": {
        "target": "structure_preference",
        "type": "mcq",
        "mapping": {
            "A": "narrative",
            "B": "structured",
        },
        "default": "structured"
    },

    "35": {
        "target": "example_type_preference",
        "type": "mcq",
        "mapping": {
            "A": "real-world",
            "B": "abstract",
        },
        "default": "real-world"
    },


    # -------------------------------------------------------------
    # SECTION 5 — EMOTIONS & STUDY BEHAVIOR
    # -------------------------------------------------------------

    "36": {
        "target": "stuck_frequency",
        "type": "rating",
        "scale": 10,
        "default": 5
    },

    "37": {
        "target": "post_challenge_behavior",
        "type": "mcq",
        "mapping": {
            "Continue with the next problem": "continue",
            "Take a short break": "break",
            "Stop studying": "stop",
        },
        "default": "continue"
    },

    "38": {
        "target": "mood_sharing_comfort",
        "type": "rating",
        "scale": 10,
        "default": 5
    },

    "39": {
        "target": "overwhelm_support_preference",
        "type": "mcq",
        "mapping": {
            "Encouragement": "encouragement",
            "Step-by-step structure": "step-by-step",
            "Short break suggestions": "break",
        },
        "default": "step-by-step"
    },

    "40": {
        "target": "study_method_confidence",
        "type": "rating",
        "scale": 10,
        "default": 5
    },

    "41": {
        "target": "stress_response",
        "type": "mcq",
        "mapping": {
            "I try to push through it immediately": "push-through",
            "I take a short pause to reset": "pause",
            "I avoid the task temporarily": "avoid",
            "It depends on the situation": "depends",
        },
        "default": "pause"
    },

    "42": {
        "target": "help_seeking_behavior",
        "type": "mcq",
        "mapping": {
            "Very comfortable": "very-comfortable",
            "Comfortable": "comfortable",
            "Slightly uncomfortable": "slightly-uncomfortable",
            "Very uncomfortable": "very-uncomfortable",
        },
        "default": "comfortable"
    },

    "43": {
        "target": "motivation_drain",
        "type": "mcq",
        "mapping": {
            "Feeling confused": "confusion",
            "Feeling overwhelmed": "overwhelm",
            "Not seeing progress": "lack-progress",
            "Lack of interest in the topic": "low-interest",
        },
        "default": "lack-progress"
    },

    "44": {
        "target": "focus_recovery_strategy",
        "type": "mcq",
        "mapping": {
            "Short breaks": "short-break",
            "Changing to an easier task": "task-switch",
            "Reviewing goals": "goal-review",
            "External reminders or prompts": "external-reminder",
        },
        "default": "short-break"
    },

    "45": {
        "target": "tone_sensitivity",
        "type": "rating",
        "scale": 10,
        "default": 5
    },

    "46": {
        "target": "post_confidence_behavior",
        "type": "mcq",
        "mapping": {
            "Move on to a harder topic": "advance",
            "Reinforce with a few more questions": "reinforce",
            "Review quickly and switch subjects": "switch",
            "Stop for the day": "stop",
        },
        "default": "reinforce"
    },

    "47": {
        "target": "anxiety_impact",
        "type": "rating",
        "scale": 10,
        "default": 5
    },

}