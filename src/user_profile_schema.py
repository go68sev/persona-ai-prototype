"""
STRUCTURE:
- 37 fields across 5 sections
- Background (5 fields): Who they are
- Learning Preferences (14 fields): How they learn best
- Communication Style (5 fields): How to talk to them
- Emotional Patterns (8 fields): How they handle difficulty
- Study Behavior (5 fields): Patterns and habits

Last updated: December 2025
"""

USER_PROFILE_SCHEMA = {
  "learning_profile": {

    # SECTION 1 - BACKGROUND (who they are)
    "background": {
      "academic_program": "string",
      "semester": "int",
      "current_focus": "string",
      "goals": "string",
      "age": "int"
    },

    # SECTION 2 - LEARNING PREFERENCES (how they learn best)
    "learning_preferences": {
      "explanation_preference": ["step-by-step", "high-level", "mixed"],
      "examples_preference": ["examples-first", "theory-first", "mixed"],
      "example_type": ["real-world", "mathematical", "code-based", "analogies", "diagrams", "mixed"],
      "example_quantity": ["multiple", "one-strong"],
      "detail_level": "int (1-10)",
      "guidance_preference": ["structured", "independent", "balanced"],
      "focus_style": ["explorer", "focused", "balanced"],
      "uses_analogies": "bool",
      "presentation_style": ["visual", "verbal", "mixed"],
      "practice_problems": "bool",
      "code_examples": ["yes", "if-necessary", "no"],
      "pacing": ["fast", "moderate", "slow-thorough"],
      "learner_type": ["analytical", "intuitive", "example-driven", "pattern-based", "sequential"],
      "repetition_preference": ["spaced-repetition", "repeated-summaries", "minimal-repetition"]
    },

    # SECTION 3 - COMMUNICATION STYLE (how to talk to them)
    "communication_style": {
      "tone": ["formal", "conversational"],
      "feedback_style": ["supportive-gentle", "supportive-direct", "direct-critical"],
      "response_depth": ["quick", "detailed"],
      "question_engagement": "bool",
      "summaries_after_explanation": "bool",

    },

    # SECTION 4 - EMOTIONAL PATTERNS (how they handle difficulty)
    "emotional_patterns": {
      "stress_response": ["push-through", "pause", "avoid", "depends"],
      "overwhelm_support": ["encouragement", "step-by-step", "break"],
      "confidence_level": "int (1-10)",
      "mood_sharing_comfort": "int (1-10)",
      "help_seeking_comfort": "int (1-10)",
      "motivation_drivers": "string",
      "common_blockers": "string",
      "learning_challenges": "string",  
    },

    # SECTION 5 - STUDY BEHAVIOR (patterns and habits)
    "study_behavior": {
      "study_rhythm": ["regular", "cramming", "mixed"],
      "focus_duration": "string",
      "attention_span": "int (1-10)",
      "recovery_strategy": ["short-break", "task-switch", "goal-review", "external-reminder"],
      "mistake_handling": ["immediate-fix", "deferred"]
    },

    # SUMMARY
    "summary": "string"
  }
}
