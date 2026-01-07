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

STRUCTURE:
- Part 1: Schema fields organized by section, each linked to interview questions
- Part 2: Quick reference summary of all valid values

Last updated: December 2025
"""

# ============================================================================
# PART 1: SCHEMA FIELDS → LINKED INTERVIEW QUESTIONS
# ============================================================================

# ============================================================
# SECTION 1: BACKGROUND
# Who the student is
# ============================================================

BACKGROUND_FIELDS = {
    "academic_program": {
        "type": "string",
        "description": "Student's degree/program name",
        "example": "Computer Science, Bachelor's",
        "linked_questions": [
            {
                "section": "Section 1 – Personal Background",
                "question": "What are you studying?",
                "type": "text"
            }
        ]
    },

    "semester": {
        "type": "integer",
        "description": "Current semester number",
        "example": 4,
        "linked_questions": [
            {
                "section": "Section 1 – Personal Background",
                "question": "What semester are you currently in?",
                "type": "text"
            }
        ]
    },

    "current_focus": {
        "type": "string",
        "description": "Current subjects/courses they're taking",
        "example": "Data Structures, Algorithms, Database Systems",
        "linked_questions": [
            {
                "section": "Section 1 – Personal Background",
                "question": "Which subjects are you taking this semester?",
                "type": "text"
            },
            {
                "section": "Section 1 – Personal Background",
                "question": "Which subjects do you enjoy the most, and why?",
                "type": "text"
            }
        ]
    },

    "goals": {
        "type": "string",
        "description": "Academic goals for the semester",
        "example": "Pass algorithms exam with good grade, understand recursion deeply",
        "linked_questions": [
            {
                "section": "Section 1 – Personal Background",
                "question": "Imagine it's the end of this semester and you're really satisfied with how things went. What would that look like? What specific goals or outcomes would make you feel successful?",
                "type": "text"
            }
        ]
    },

    "age": {
        "type": "integer",
        "description": "Student's age (optional field)",
        "example": 21,
        "linked_questions": [
            {
                "section": "Section 1 – Personal Background",
                "question": "(Optional) How old are you?",
                "type": "text"
            }
        ]
    }
}


# ============================================================
# SECTION 2: LEARNING PREFERENCES
# How the student learns best
# ============================================================

LEARNING_PREFERENCES_FIELDS = {
    "explanation_preference": {
        "type": "categorical",
        "valid_values": ["step-by-step", "high-level", "mixed"],
        "description": "How they prefer explanations structured",
        "value_meanings": {
            "step-by-step": "Detailed, sequential explanations",
            "high-level": "Overview/big picture first",
            "mixed": "Depends on topic complexity"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "How do you prefer textual explanations?",
                "type": "text",
                "placeholder": "e.g. Step-by-step, high-level overview..."
            },
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which explanation structure feels more natural to you? (Narrative vs Formal)",
                "type": "mcq"
            }
        ]
    },

    "examples_preference": {
        "type": "categorical",
        "valid_values": ["examples-first", "theory-first", "mixed"],
        "description": "Whether they want examples before or after theory",
        "value_meanings": {
            "examples-first": "See concrete examples, then learn theory",
            "theory-first": "Understand concepts, then see examples",
            "mixed": "Both approaches work depending on topic"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "What type of explanation works best for you when learning something new?",
                "type": "text",
                "placeholder": "e.g. examples first, diagrams, analogies, theory, text-based explanations..."
            },
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Think about a recent time when you learned something difficult and it actually clicked...",
                "type": "text",
                "extraction_hint": "Look for mentions of 'seeing examples first' or 'understanding concept first'"
            }
        ]
    },

    "example_type": {
        "type": "categorical",
        "valid_values": ["real-world", "mathematical", "code-based", "analogies", "diagrams", "mixed"],
        "description": "What type of examples help them most",
        "value_meanings": {
            "real-world": "Practical, relatable scenarios",
            "mathematical": "Formal, numerical examples",
            "code-based": "Programming examples",
            "analogies": "Metaphors and comparisons",
            "diagrams": "Visual representations",
            "mixed": "Multiple types depending on topic"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "What type of explanation works best for you when learning something new?",
                "type": "text"
            },
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which type of examples do you prefer when practicing? (Real-world vs Abstract)",
                "type": "mcq"
            }
        ]
    },

    "example_quantity": {
        "type": "categorical",
        "valid_values": ["multiple", "one-strong"],
        "description": "Whether they prefer multiple examples or one strong example",
        "value_meanings": {
            "multiple": "Prefer seeing several examples to understand different angles",
            "one-strong": "Prefer one well-explained, comprehensive example"
        },
        "linked_questions": [
            {
                "section": "Section 3 – Content Preferences",
                "question": "For examples, you prefer:",
                "type": "mcq",
                "options": ["Multiple examples", "One strong example"]
            }
        ]
    },

    "detail_level": {
        "type": "scale",
        "range": "1-10",
        "description": "How detailed they want explanations (1=brief, 10=very detailed)",
        "example": 7,
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "How detailed do you like explanations?",
                "type": "rating",
                "scale": "0-10 (brief to very detailed)"
            }
        ]
    },

    "guidance_preference": {
        "type": "categorical",
        "valid_values": ["structured", "independent", "balanced"],
        "description": "How much guidance vs independence they want",
        "value_meanings": {
            "structured": "Clear guidance, step-by-step direction",
            "independent": "Prefer to explore and figure out on their own",
            "balanced": "Mix of guidance and self-discovery"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Describe a recent study session that felt really productive. How much guidance did you have versus figuring things out yourself?",
                "type": "text"
            }
        ]
    },

    "focus_style": {
        "type": "categorical",
        "valid_values": ["explorer", "focused", "balanced"],
        "description": "Whether they prefer exploring side topics or staying focused on main goal",
        "value_meanings": {
            "explorer": "Enjoys exploring tangents and related topics",
            "focused": "Prefers staying on track with the main objective",
            "balanced": "Mix of both depending on time/context"
        },
        "linked_questions": [
            {
                "section": "Section 4 – Comparison Questions",
                "question": "When studying, which do you prefer?",
                "type": "rating",
                "scale": "0-10 (Exploring side topics to Staying focused on main goal)",
                "extraction_hint": "0-3 = explorer, 4-6 = balanced, 7-10 = focused"
            }
        ]
    },

    "uses_analogies": {
        "type": "boolean",
        "valid_values": [True, False],
        "description": "Whether analogies and metaphors help them learn",
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "What type of explanation works best for you when learning something new?",
                "type": "text",
                "extraction_hint": "Check if they mention analogies, metaphors, or comparisons"
            },
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which explanation style helps you understand better? (Simple kid-friendly vs Technical academic)",
                "type": "mcq",
                "extraction_hint": "Option A (simple) often indicates preference for analogies"
            }
        ]
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
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "What type of explanation works best for you when learning something new?",
                "type": "text",
                "extraction_hint": "Look for mentions of diagrams, visuals, flowcharts vs text, reading"
            },
            {
                "section": "Section 3 – Content Preferences",
                "question": "Does video-based learning help you?",
                "type": "mcq",
                "extraction_hint": "Yes to video often correlates with visual preference"
            }
        ]
    },

    "practice_problems": {
        "type": "boolean",
        "valid_values": [True, False],
        "description": "Whether they want practice problems included in explanations",
        "linked_questions": [
            {
                "section": "Section 3 – Content Preferences",
                "question": "Should explanations include practice problems?",
                "type": "mcq",
                "options": ["Yes", "Maybe later", "No"]
            }
        ]
    },

    "code_examples": {
        "type": "categorical",
        "valid_values": ["yes", "if-necessary", "no"],
        "description": "Whether they want code examples for technical topics",
        "value_meanings": {
            "yes": "Always include code examples",
            "if-necessary": "Only when directly relevant",
            "no": "Prefer conceptual explanations without code"
        },
        "linked_questions": [
            {
                "section": "Section 3 – Content Preferences",
                "question": "For technical topics, do you want code examples?",
                "type": "mcq",
                "options": ["Yes", "Only if necessary", "No"]
            }
        ]
    },

    "pacing": {
        "type": "categorical",
        "valid_values": ["fast", "moderate", "slow-thorough"],
        "description": "Preferred learning pace",
        "value_meanings": {
            "fast": "Quick pace, hit key points",
            "moderate": "Balanced pace",
            "slow-thorough": "Take time, ensure deep understanding"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Think about a recent time when you learned something difficult and it actually clicked...",
                "type": "text",
                "extraction_hint": "Infer from their description of successful learning pace"
            },
            {
                "section": "Section 6 – Situational",
                "question": "You've set aside 3 hours to study for an algorithms exam. Describe exactly how you would structure those 3 hours...",
                "type": "text",
                "extraction_hint": "Infer from how they break down time and pace themselves"
            }
        ]
    },

    "learner_type": {
        "type": "categorical",
        "valid_values": ["analytical", "intuitive", "example-driven", "pattern-based", "sequential"],
        "description": "Primary learning style/approach",
        "value_meanings": {
            "analytical": "Breaks down problems logically, wants to understand 'why'",
            "intuitive": "Grasps concepts quickly, comfortable with ambiguity",
            "example-driven": "Learns best through concrete examples",
            "pattern-based": "Looks for patterns and connections",
            "sequential": "Prefers linear, step-by-step progression"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Think about a recent time when you learned something difficult and it actually clicked...",
                "type": "text",
                "extraction_hint": "Infer learner type from their described approach"
            },
            {
                "section": "Section 2 – Learning Preferences",
                "question": "What type of explanation works best for you when learning something new?",
                "type": "text"
            },
            {
                "section": "Section 6 – Situational",
                "question": "After studying a topic, how do you check that you truly understand it?",
                "type": "text",
                "extraction_hint": "Method of verification reveals learning style"
            }
        ]
    },

    "repetition_preference": {
        "type": "categorical",
        "valid_values": ["spaced-repetition", "repeated-summaries", "minimal-repetition"],
        "description": "How they prefer to reinforce learning",
        "value_meanings": {
            "spaced-repetition": "Review at intervals over time",
            "repeated-summaries": "Multiple summaries/reviews in one session",
            "minimal-repetition": "Understand once, move on"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "For memorization, what works best for you?",
                "type": "text",
                "placeholder": "e.g. Flashcards, Summaries, Mnemonics..."
            }
        ]
    }
}


# ============================================================
# SECTION 3: COMMUNICATION STYLE
# How the AI should communicate with them
# ============================================================

COMMUNICATION_STYLE_FIELDS = {
    "tone": {
        "type": "categorical",
        "valid_values": ["formal", "conversational"],
        "description": "Preferred writing/communication style",
        "value_meanings": {
            "formal": "Academic, professional language",
            "conversational": "Friendly, casual language"
        },
        "linked_questions": [
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which writing style helps you more?",
                "type": "rating",
                "scale": "0-10 (Formal academic to Friendly conversational)"
            },
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which explanation style helps you understand better? (Simple vs Technical)",
                "type": "mcq"
            }
        ]
    },

    "feedback_style": {
        "type": "categorical",
        "valid_values": ["supportive-gentle", "supportive-direct", "direct-critical"],
        "description": "How they want feedback delivered",
        "value_meanings": {
            "supportive-gentle": "Encouraging, soft corrections with praise",
            "supportive-direct": "Kind but clear about what's wrong",
            "direct-critical": "Straightforward, no sugarcoating"
        },
        "linked_questions": [
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which feedback style helps you improve faster? (Encouraging vs Direct)",
                "type": "rating",
                "scale": "0-10 (Encouraging & supportive to Direct & corrective)"
            },
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Which learning challenge do you prefer when practicing?",
                "type": "mcq",
                "options": ["Encouraging & supportive feedback", "Direct & corrective feedback"]
            }
        ]
    },

    "response_depth": {
        "type": "categorical",
        "valid_values": ["quick", "detailed"],
        "description": "Preferred response length/depth",
        "value_meanings": {
            "quick": "Brief, to-the-point answers",
            "detailed": "Thorough, comprehensive explanations"
        },
        "linked_questions": [
            {
                "section": "Section 4 – Comparison Questions",
                "question": "For answers, you prefer:",
                "type": "mcq",
                "options": ["Quick response", "Deep explanation"]
            }
        ]
    },

    "question_engagement": {
        "type": "boolean",
        "valid_values": [True, False],
        "description": "Whether the AI should ask questions to engage thinking",
        "linked_questions": [
            {
                "section": "Section 4 – Comparison Questions",
                "question": "Do you like when the system asks you to engage your thinking, and how?",
                "type": "text",
                "placeholder": "e.g. Questions after explanation, quizzes..."
            }
        ]
    },

    "summaries_after_explanation": {
        "type": "boolean",
        "valid_values": [True, False],
        "description": "Whether they want summaries after explanations",
        "linked_questions": [
            {
                "section": "Section 3 – Content Preferences",
                "question": "Do you want summaries after explanations?",
                "type": "mcq",
                "options": ["Yes", "Sometimes", "No"]
            }
        ]
    }
}


# ============================================================
# SECTION 4: EMOTIONAL PATTERNS
# How they handle difficulty and emotions while learning
# ============================================================

EMOTIONAL_PATTERNS_FIELDS = {
    "stress_response": {
        "type": "categorical",
        "valid_values": ["push-through", "pause", "avoid", "depends"],
        "description": "How they react when stressed or stuck",
        "value_meanings": {
            "push-through": "Keeps working despite stress",
            "pause": "Takes breaks to reset mentally",
            "avoid": "Tends to switch to easier tasks or avoid",
            "depends": "Varies by situation and stress level"
        },
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "When you feel stuck studying, what is your first reaction?",
                "type": "text",
                "placeholder": "e.g. push through, short reset break, avoiding tasks..."
            }
        ]
    },

    "overwhelm_support": {
        "type": "categorical",
        "valid_values": ["encouragement", "step-by-step", "break"],
        "description": "What helps when they feel overwhelmed",
        "value_meanings": {
            "encouragement": "Emotional support and motivation",
            "step-by-step": "Breaking down into smaller, manageable pieces",
            "break": "Stepping away temporarily to reset"
        },
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "When overwhelmed, what helps more?",
                "type": "text",
                "placeholder": "e.g. encouragement, step-by-step structure..."
            }
        ]
    },

    "confidence_level": {
        "type": "scale",
        "range": "1-10",
        "description": "Confidence in their current study methods (1=low, 10=high)",
        "example": 6,
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "How confident are you in your current study methods?",
                "type": "rating",
                "scale": "1-10 (not confident to very confident)"
            }
        ]
    },

    "mood_sharing_comfort": {
        "type": "scale",
        "range": "1-10",
        "description": "How comfortable they are sharing their mood/emotions with the system (1=very uncomfortable, 10=very comfortable)",
        "example": 5,
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "How comfortable are you sharing your mood with the system?",
                "type": "rating",
                "scale": "0-10 (very uncomfortable to very comfortable)"
            }
        ]
    },

    "help_seeking_comfort": {
        "type": "scale",
        "range": "1-10",
        "description": "How comfortable they are asking for help when stuck (1=very uncomfortable, 10=very comfortable)",
        "example": 6,
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "How do you feel about asking for help when you're stuck?",
                "type": "rating",
                "scale": "0-10 (very uncomfortable to very comfortable)"
            }
        ]
    },

    "motivation_drivers": {
        "type": "string",
        "description": "What motivates them to keep learning",
        "example": "Seeing progress, solving challenging problems, real-world applications",
        "linked_questions": [
            {
                "section": "Section 1 – Personal Background",
                "question": "Which subjects do you enjoy the most, and why?",
                "type": "text",
                "extraction_hint": "The 'why' reveals motivation drivers"
            },
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Think about a recent time when you learned something difficult and it actually clicked...",
                "type": "text",
                "extraction_hint": "What made it satisfying reveals motivators"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "When you feel confident about a topic, what do you prefer to do next?",
                "type": "text"
            }
        ]
    },

    "common_blockers": {
        "type": "string",
        "description": "What typically blocks their progress or drains motivation",
        "example": "Confusion without clear next steps, feeling overwhelmed, lack of progress",
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Now think about a time when learning felt harder than expected. What was happening? What made it difficult?",
                "type": "text"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "When do you usually feel stuck when learning?",
                "type": "text"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "What usually drains your motivation the most?",
                "type": "text"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "List any problems you find with your current study methods?",
                "type": "text"
            }
        ]
    },

    "learning_challenges": {
        "type": "string",
        "description": "Specific challenges they face when learning",
        "example": "Staying focused for long periods, understanding abstract concepts",
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "Now think about a time when learning felt harder than expected...",
                "type": "text"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "List any problems you find with your current study methods?",
                "type": "text"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "How often does anxiety impact your learning?",
                "type": "rating",
                "scale": "0-10"
            }
        ]
    }
}


# ============================================================
# SECTION 5: STUDY BEHAVIOR
# Study habits and patterns
# ============================================================

STUDY_BEHAVIOR_FIELDS = {
    "study_rhythm": {
        "type": "categorical",
        "valid_values": ["regular", "cramming", "mixed"],
        "description": "Study pattern over the semester",
        "value_meanings": {
            "regular": "Consistent study throughout semester",
            "cramming": "Intensive study close to deadlines/exams",
            "mixed": "Combination depending on subject/deadline"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "What does your study rhythm currently look like over the semester, and how would you ideally like it to be?",
                "type": "text"
            },
            {
                "section": "Section 6 – Situational",
                "question": "It's Sunday evening and you have three assignments due this week... Describe how you would plan and execute your week.",
                "type": "text"
            }
        ]
    },

    "focus_duration": {
        "type": "string",
        "description": "How long they can focus in one session before needing a break",
        "example": "45-60 minutes",
        "linked_questions": [
            {
                "section": "Section 6 – Situational",
                "question": "You've set aside 3 hours to study for an algorithms exam. Describe exactly how you would structure those 3 hours...",
                "type": "text",
                "extraction_hint": "Look for how they break up study blocks"
            },
            {
                "section": "Section 6 – Situational",
                "question": "Describe your ideal study environment and learning session...",
                "type": "text"
            }
        ]
    },

    "attention_span": {
        "type": "scale",
        "range": "1-10",
        "description": "How easily distracted vs focused (1=very distracted, 10=very focused)",
        "example": 6,
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "How often do you feel stuck when learning?",
                "type": "rating",
                "extraction_hint": "High stuck frequency may indicate attention challenges"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "What helps you regain focus after getting distracted?",
                "type": "text",
                "extraction_hint": "Frequency of needing this indicates attention span"
            },
            {
                "section": "Section 6 – Situational",
                "question": "Describe your ideal study environment...",
                "type": "text",
                "extraction_hint": "Environment needs reveal focus requirements"
            }
        ]
    },

    "recovery_strategy": {
        "type": "categorical",
        "valid_values": ["short-break", "task-switch", "goal-review", "external-reminder"],
        "description": "How they regain focus after distraction",
        "value_meanings": {
            "short-break": "Takes brief 5-10 minute breaks",
            "task-switch": "Changes to a different or easier task",
            "goal-review": "Reminds themselves of goals/why they're studying",
            "external-reminder": "Uses external tools, alarms, or accountability"
        },
        "linked_questions": [
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "What helps you regain focus after getting distracted?",
                "type": "text"
            },
            {
                "section": "Section 5 – Academic Emotions & Study Behavior",
                "question": "What do you normally do after solving something challenging?",
                "type": "text"
            }
        ]
    },

    "mistake_handling": {
        "type": "categorical",
        "valid_values": ["immediate-fix", "deferred"],
        "description": "How they handle mistakes when learning",
        "value_meanings": {
            "immediate-fix": "Stop and fix mistakes right away",
            "deferred": "Note mistakes, move on, revisit later"
        },
        "linked_questions": [
            {
                "section": "Section 2 – Learning Preferences",
                "question": "How do you typically proceed after making a mistake?",
                "type": "text"
            }
        ]
    }
}


# ============================================================================
# PART 2: QUICK REFERENCE SUMMARY
# ============================================================================
# Use this as a cheat sheet when reviewing extracted profiles


VALID_VALUES_SUMMARY = {
    # ===================
    # CATEGORICAL FIELDS
    # ===================

    # Learning Preferences
    "explanation_preference": ["step-by-step", "high-level", "mixed"],
    "examples_timing": ["examples-first", "theory-first", "mixed"],
    "example_type": ["real-world", "mathematical", "code-based", "analogies", "diagrams", "mixed"],
    "guidance_preference": ["structured", "independent", "balanced"],
    "presentation_style": ["visual", "verbal", "mixed"],
    "code_examples": ["yes", "if-necessary", "no"],
    "pacing": ["fast", "moderate", "slow-thorough"],
    "learner_type": ["analytical", "intuitive", "example-driven", "pattern-based", "sequential"],
    "repetition_preference": ["spaced-repetition", "repeated-summaries", "minimal-repetition"],

    # Communication Style
    "tone": ["formal", "conversational"],
    "feedback_style": ["supportive-gentle", "supportive-direct", "direct-critical"],
    "response_depth": ["quick", "detailed"],

    # Emotional Patterns
    "stress_response": ["push-through", "pause", "avoid", "depends"],
    "overwhelm_support": ["encouragement", "step-by-step", "break"],

    # Study Behavior
    "study_rhythm": ["regular", "cramming", "mixed"],
    "recovery_strategy": ["short-break", "task-switch", "goal-review", "external-reminder"],
    "mistake_handling": ["immediate-fix", "deferred"],

    # ===================
    # SCALE FIELDS (1-10)
    # ===================
    "detail_level": "1-10 (1=brief, 10=very detailed)",
    "confidence_level": "1-10 (1=not confident, 10=very confident)",
    "attention_span": "1-10 (1=easily distracted, 10=very focused)",

    # ===================
    # BOOLEAN FIELDS
    # ===================
    "uses_analogies": [True, False],
    "practice_problems": [True, False],
    "question_engagement": [True, False],
    "summaries_after_explanation": [True, False],

    # ===================
    # STRING FIELDS
    # ===================
    "academic_program": "Free text - degree/program name",
    "current_focus": "Free text - current subjects",
    "goals": "Free text - academic goals",
    "focus_duration": "Free text - e.g., '45-60 minutes'",
    "motivation_drivers": "Free text - what motivates them",
    "common_blockers": "Free text - what blocks progress",
    "learning_challenges": "Free text - specific challenges faced",

    # ===================
    # INTEGER FIELDS
    # ===================
    "semester": "Integer - current semester number",
    "age": "Integer - student's age (optional)"
}