USER_PROFILE_SCHEMA = {

    "personal_background": {
        "academic_program": str,                 
        "current_courses": list,
        "semester": int,
        "academic_goals": str,                   
        "favorite_subjects": (str, list),
        "age": int                             
    },

    # SECTION 2 — LEARNING PREFERENCES

    "learning_preferences": {
        "examples_vs_theory": ("examples-first", "theory-first", "mixed"),
        "visual_vs_verbal": ("visual", "verbal", "mixed"),
        "uses_analogies": (bool, str),
        "explanation_preference": ("step-by-step", "high-level", "mixed"),
        "guidance_preference": ("structured", "independent", "balanced"),
        "learning_mode": ("practice", "conceptual"),
        "memorization_strategy": ("flashcards", "summaries", "mnemonics", "other"),
        "study_rhythm": ("regular", "cram", "mixed"),
        "detail_level": int,
        "mistake_handling": ("immediate-fix", "deferred"),
        "review_style": ("spaced", "intensive", "depends"),
        "flashcard_preference": (bool, str)
    },

    # SECTION 3 — CONTENT PREFERENCES

    "content_preferences": {
        "video_learning": (bool, str),
        "code_examples": ("yes", "if-necessary", "no"),
        "example_quantity": ("multiple", "single"),
        "practice_problems": (bool, str),
        "input_modality": ("reading", "audio", "mixed"),
        "summary_preference": (bool, str),
        "diagram_preference": (bool, str)
    },

    # SECTION 4 — COMMUNICATION STYLE

    "communication_style": {
        "response_depth": ("quick", "deep"),
        "question_engagement": bool,
        "writing_style": ("formal", "conversational"),
        "study_focus": ("exploratory", "focused"),
        "explanation_style": ("simple", "technical"),
        "format_preference": ("visual", "verbal"),
        "learning_approach": ("active", "reflective"),
        "feedback_style": ("supportive", "direct"),
        "structure_preference": ("narrative", "structured"),
        "example_type_preference": ("real-world", "abstract")
    },

    # SECTION 5 — ACADEMIC EMOTIONS & STUDY BEHAVIOR

    "academic_emotions_and_behavior": {
        "stuck_frequency": int,
        "post_challenge_behavior": ("continue", "break", "stop"),
        "mood_sharing_comfort": int,
        "overwhelm_support_preference": ("encouragement", "step-by-step", "break"),
        "study_method_confidence": int, 
        "stress_response": ("push-through", "pause", "avoid", "depends"),
        "help_seeking_behavior": (
            "very-comfortable",
            "comfortable",
            "slightly-uncomfortable",
            "very-uncomfortable"
        ),
        "motivation_drain": (
            "confusion",
            "overwhelm",
            "lack-progress",
            "low-interest"
        ),
        "focus_recovery_strategy": (
            "short-break",
            "task-switch",
            "goal-review",
            "external-reminder"
        ),
        "tone_sensitivity": int,               
        "post_confidence_behavior": (
            "advance",
            "reinforce",
            "switch",
            "stop"
        ),
        "anxiety_impact": int 
    }
}
