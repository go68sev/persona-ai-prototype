"""
preference_parameters.py - Documentation Reference

PURPOSE:
This file serves as DOCUMENTATION for the team to understand:
1. What fields exist in the user profile schema
2. What valid values each field can have
3. Which interview questions map to which profile fields

NOTE: This file is NOT used by the extraction code!
The LLM (GPT-4o-mini) reads interview responses and extracts values directly.
This file is for HUMAN REFERENCE only - to help the team understand the system.

Last updated: 2025
"""

# ============================================================
# SECTION 1: BACKGROUND
# ============================================================
# These fields capture basic info about the student

BACKGROUND_FIELDS = {
    "academic_program": {
        "type": "string",
        "description": "Student's degree/program name",
        "example": "Computer Science, Bachelor's",
        "interview_questions": ["Q1: What are you studying?"]
    },

    "semester": {
        "type": "integer",
        "description": "Current semester number",
        "example": 4,
        "interview_questions": ["Q3: What semester are you currently in?"]
    },

    "current_focus": {
        "type": "string",
        "description": "What they're currently learning/struggling with",
        "example": "Data Structures, Algorithms",
        "interview_questions": ["Q2: Which subjects are you taking?"]
    },

    "goals": {
        "type": "string",
        "description": "Academic goals for the semester",
        "example": "Pass algorithms exam, understand recursion",
        "interview_questions": ["Q4: What are your academic goals?"]
    },

    "age": {
        "type": "integer",
        "description": "Student's age (optional)",
        "example": 21,
        "interview_questions": ["Q6: How old are you?"]
    }
}


# ============================================================
# SECTION 2: LEARNING PREFERENCES
# ============================================================
# These fields capture how the student prefers to learn

LEARNING_PREFERENCES_FIELDS = {
    "explanation_preference": {
        "type": "categorical",
        "valid_values": ["step-by-step", "high-level", "mixed"],
        "description": "How they prefer explanations structured",
        "value_meanings": {
            "step-by-step": "Detailed, sequential explanations",
            "high-level": "Overview/big picture first",
            "mixed": "Depends on topic"
        },
        "interview_questions": ["Q10: How do you prefer textual explanations?"]
    },

    "examples_preference": {
        "type": "categorical",
        "valid_values": ["examples-first", "theory-first", "mixed"],
        "description": "Whether they want examples before or after theory",
        "value_meanings": {
            "examples-first": "See concrete examples, then learn theory",
            "theory-first": "Understand concepts, then see examples",
            "mixed": "Both approaches work"
        },
        "interview_questions": ["Q9: What type of explanation works best?", "Q7/Q8: Learning moments"]
    },

    "detail_level": {
        "type": "scale",
        "range": "1-10",
        "description": "How detailed they want explanations (1=brief, 10=very detailed)",
        "example": 7,
        "interview_questions": ["Q15: How detailed do you like explanations?"]
    },

    "guidance_preference": {
        "type": "categorical",
        "valid_values": ["structured", "independent", "balanced"],
        "description": "How much guidance they want",
        "value_meanings": {
            "structured": "Clear guidance and direction",
            "independent": "Explore on their own",
            "balanced": "Mix of both"
        },
        "interview_questions": ["Q11: How guided or independent do you like learning?"]
    },

    "uses_analogies": {
        "type": "boolean",
        "valid_values": [True, False, "sometimes"],
        "description": "Whether analogies help them learn",
        "interview_questions": ["Q9: mentions analogies", "Q7/Q8: Learning moments"]
    },

    "presentation_style": {
        "type": "categorical",
        "valid_values": ["visual", "verbal", "mixed"],
        "description": "Visual (diagrams) vs verbal (text) preference",
        "value_meanings": {
            "visual": "Prefers diagrams, charts, visual aids",
            "verbal": "Prefers text-based explanations",
            "mixed": "Comfortable with both"
        },
        "interview_questions": ["Q9: mentions diagrams/visuals"]
    },

    "practice_problems": {
        "type": "boolean",
        "valid_values": [True, False, "sometimes"],
        "description": "Whether they want practice problems included",
        "interview_questions": ["Q20: Should explanations include practice problems?"]
    },

    "code_examples": {
        "type": "categorical",
        "valid_values": ["yes", "if-necessary", "no"],
        "description": "Whether they want code examples",
        "value_meanings": {
            "yes": "Always include code",
            "if-necessary": "Only when relevant",
            "no": "Prefer conceptual explanations"
        },
        "interview_questions": ["Q18: Do you want code examples?"]
    }
}


# ============================================================
# SECTION 3: COMMUNICATION STYLE
# ============================================================
# These fields capture how the AI should communicate

COMMUNICATION_STYLE_FIELDS = {
    "tone": {
        "type": "categorical",
        "valid_values": ["formal", "conversational"],
        "description": "Preferred writing style",
        "value_meanings": {
            "formal": "Academic, professional language",
            "conversational": "Friendly, casual language"
        },
        "interview_questions": ["Q24: Which writing style helps you more?"]
    },

    "feedback_style": {
        "type": "categorical",
        "valid_values": ["supportive", "direct"],
        "description": "How they want feedback delivered",
        "value_meanings": {
            "supportive": "Encouraging, gentle corrections",
            "direct": "Straightforward, tells exactly what's wrong"
        },
        "interview_questions": ["Q27: Which feedback style helps you improve?"]
    },

    "response_depth": {
        "type": "categorical",
        "valid_values": ["quick", "detailed"],
        "description": "Preferred response length",
        "value_meanings": {
            "quick": "Brief, to-the-point answers",
            "detailed": "Thorough, comprehensive explanations"
        },
        "interview_questions": ["Q22: Quick response or deep explanation?"]
    },

    "question_engagement": {
        "type": "boolean",
        "valid_values": [True, False],
        "description": "Whether AI should ask questions back",
        "interview_questions": ["Q23: Do you like when system asks you questions?"]
    }
}


# ============================================================
# SECTION 4: EMOTIONAL PATTERNS
# ============================================================
# These fields capture emotional responses to learning

EMOTIONAL_PATTERNS_FIELDS = {
    "stress_response": {
        "type": "categorical",
        "valid_values": ["push-through", "pause", "avoid", "depends"],
        "description": "How they react when stressed",
        "value_meanings": {
            "push-through": "Keeps working despite stress",
            "pause": "Takes breaks to reset",
            "avoid": "Tends to avoid stressful tasks",
            "depends": "Varies by situation"
        },
        "interview_questions": ["Section 5: When stuck, what is your first reaction?"]
    },

    "overwhelm_support": {
        "type": "categorical",
        "valid_values": ["encouragement", "step-by-step", "break"],
        "description": "What helps when overwhelmed",
        "value_meanings": {
            "encouragement": "Emotional support and motivation",
            "step-by-step": "Breaking down into smaller pieces",
            "break": "Stepping away temporarily"
        },
        "interview_questions": ["Section 5: When overwhelmed, what helps more?"]
    },

    "confidence_level": {
        "type": "scale",
        "range": "1-10",
        "description": "Confidence in their study methods (1=low, 10=high)",
        "example": 6,
        "interview_questions": ["Section 5: How confident in your study methods?"]
    },

    "motivation_drivers": {
        "type": "string",
        "description": "What motivates them to keep learning",
        "example": "Seeing progress, solving problems, real-world applications",
        "interview_questions": ["Inferred from Q7, Q5, situational questions"]
    },

    "common_blockers": {
        "type": "string",
        "description": "What drains their motivation",
        "example": "Confusion, lack of progress, overwhelm",
        "interview_questions": ["Section 5: What drains your motivation?"]
    }
}


# ============================================================
# SECTION 5: STUDY BEHAVIOR
# ============================================================
# These fields capture study habits and patterns

STUDY_BEHAVIOR_FIELDS = {
    "study_rhythm": {
        "type": "categorical",
        "valid_values": ["regular", "cramming", "mixed"],
        "description": "Study pattern over the semester",
        "value_meanings": {
            "regular": "Consistent study throughout",
            "cramming": "Intensive study near deadlines",
            "mixed": "Combination of both"
        },
        "interview_questions": ["Q14: What does your study rhythm look like?"]
    },

    "focus_duration": {
        "type": "string",
        "description": "How long they can focus in one session",
        "example": "45-60 minutes",
        "interview_questions": ["Situational: 3-hour study session breakdown"]
    },

    "attention_span": {
        "type": "scale",
        "range": "1-10",
        "description": "How easily distracted (1=very distracted, 10=very focused)",
        "example": 6,
        "interview_questions": ["Inferred from situational questions, focus recovery"]
    },

    "recovery_strategy": {
        "type": "categorical",
        "valid_values": ["short-break", "task-switch", "goal-review", "external-reminder"],
        "description": "How they regain focus after distraction",
        "value_meanings": {
            "short-break": "Takes brief 5-10 minute breaks",
            "task-switch": "Changes to different/easier task",
            "goal-review": "Reminds themselves of goals",
            "external-reminder": "Uses external prompts/tools"
        },
        "interview_questions": ["Section 5: What helps you regain focus?"]
    },

    "mistake_handling": {
        "type": "categorical",
        "valid_values": ["immediate-fix", "deferred"],
        "description": "How they handle mistakes",
        "value_meanings": {
            "immediate-fix": "Fix mistakes right away",
            "deferred": "Move on, revisit later"
        },
        "interview_questions": ["Q16: How do you proceed after making a mistake?"]
    }
}


# ============================================================
# QUICK REFERENCE: ALL VALID VALUES
# ============================================================
# Use this as a cheat sheet when reviewing extracted profiles

VALID_VALUES_SUMMARY = {
    # Categorical fields
    "explanation_preference": ["step-by-step", "high-level", "mixed"],
    "examples_preference": ["examples-first", "theory-first", "mixed"],
    "guidance_preference": ["structured", "independent", "balanced"],
    "presentation_style": ["visual", "verbal", "mixed"],
    "code_examples": ["yes", "if-necessary", "no"],
    "tone": ["formal", "conversational"],
    "feedback_style": ["supportive", "direct"],
    "response_depth": ["quick", "detailed"],
    "stress_response": ["push-through", "pause", "avoid", "depends"],
    "overwhelm_support": ["encouragement", "step-by-step", "break"],
    "study_rhythm": ["regular", "cramming", "mixed"],
    "recovery_strategy": ["short-break", "task-switch", "goal-review", "external-reminder"],
    "mistake_handling": ["immediate-fix", "deferred"],

    # Scale fields (1-10)
    "detail_level": "1-10 (1=brief, 10=very detailed)",
    "confidence_level": "1-10 (1=low, 10=high)",
    "attention_span": "1-10 (1=easily distracted, 10=very focused)",

    # Boolean fields
    "uses_analogies": [True, False, "sometimes"],
    "practice_problems": [True, False, "sometimes"],
    "question_engagement": [True, False]
}


# ============================================================
# INTERVIEW QUESTION → SCHEMA FIELD MAPPING
# ============================================================
# Quick reference: which questions inform which fields

QUESTION_TO_FIELD_MAPPING = {
    # Section 1 - Background
    "Q1 (studying)": "background.academic_program",
    "Q2 (subjects)": "background.current_focus",
    "Q3 (semester)": "background.semester",
    "Q4 (goals)": "background.goals",
    "Q5 (favorite subjects)": "background.current_focus, emotional_patterns.motivation_drivers",
    "Q6 (age)": "background.age",
    "Q7 (good learning moment)": "learning_preferences.examples_preference, learning_preferences.presentation_style",
    "Q8 (difficult moment)": "emotional_patterns.common_blockers, learning_preferences.explanation_preference",

    # Section 2 - Learning Preferences
    "Q9 (explanation type)": "learning_preferences.examples_preference, learning_preferences.presentation_style, learning_preferences.uses_analogies",
    "Q10 (textual preference)": "learning_preferences.explanation_preference",
    "Q11 (guidance level)": "learning_preferences.guidance_preference",
    "Q12 (theory:practice)": "learning_preferences.practice_problems",
    "Q13 (memorization)": "study_behavior (inferred)",
    "Q14 (study rhythm)": "study_behavior.study_rhythm",
    "Q15 (detail level)": "learning_preferences.detail_level",
    "Q16 (mistake handling)": "study_behavior.mistake_handling",

    # Section 3 - Content
    "Q17 (video)": "Not in simplified schema",
    "Q18 (code examples)": "learning_preferences.code_examples",
    "Q19 (example quantity)": "learning_preferences (inferred)",
    "Q20 (practice problems)": "learning_preferences.practice_problems",
    "Q21 (summaries)": "Not in simplified schema",

    # Section 4 - Comparison
    "Q22 (response depth)": "communication_style.response_depth",
    "Q23 (engagement)": "communication_style.question_engagement",
    "Q24 (writing style)": "communication_style.tone",
    "Q25 (explanation style)": "communication_style.tone",
    "Q26 (focus)": "study_behavior (inferred)",
    "Q27 (feedback style)": "communication_style.feedback_style",
    "Q28 (structure)": "learning_preferences.explanation_preference",
    "Q29 (example type)": "learning_preferences.examples_preference",

    # Section 5 - Emotions & Behavior
    "Stuck frequency": "emotional_patterns (inferred)",
    "When stuck": "emotional_patterns.common_blockers",
    "Stuck reaction": "emotional_patterns.stress_response",
    "Post-challenge": "study_behavior.recovery_strategy",
    "Mood comfort": "Not in simplified schema",
    "Overwhelm support": "emotional_patterns.overwhelm_support",
    "Method confidence": "emotional_patterns.confidence_level",
    "Method problems": "emotional_patterns.common_blockers",
    "Help seeking": "Not in simplified schema",
    "Motivation drain": "emotional_patterns.common_blockers",
    "Focus recovery": "study_behavior.recovery_strategy",
    "Post-confidence": "study_behavior (inferred)",
    "Anxiety impact": "Not in simplified schema",

    # Situational Questions
    "Weekly planning": "study_behavior.study_rhythm, emotional_patterns.stress_response",
    "3-hour session": "study_behavior.focus_duration, study_behavior.recovery_strategy",
    "Ideal environment": "study_behavior.attention_span, study_behavior.focus_duration",
    "Understanding check": "learning_preferences (inferred)"
}