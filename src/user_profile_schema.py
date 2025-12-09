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
      "detail_level": "int (1-10)",
      "guidance_preference": ["structured", "independent", "balanced"],
      "uses_analogies": "bool",
      "presentation_style": ["visual", "verbal", "mixed"],
      "practice_problems": "bool",
      "code_examples": ["yes", "if-necessary", "no"]
    },


    # SECTION 3 - COMMUNICATION STYLE (how to talk to them)
    "communication_style": {
      "tone": ["formal", "conversational"],
      "feedback_style": ["supportive", "direct"],
      "response_depth": ["quick", "detailed"],
      "question_engagement": "bool"
    },

    # SECTION 4 - EMOTIONAL PATTERNS (how they handle difficulty)
    "emotional_patterns": {
      "stress_response": ["push-through", "pause", "avoid", "depends"],
      "overwhelm_support": ["encouragement", "step-by-step", "break"],
      "confidence_level": "int (1-10)",
      "motivation_drivers": "string",
      "common_blockers": "string"
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
