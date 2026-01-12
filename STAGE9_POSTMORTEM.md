# Stage 9: Postmortem

**Purpose**: Consolidate knowledge before deciding whether Stage 10 should exist.

**Observation Period**: [START DATE] to [END DATE]  
**Total Days**: [COUNT]  
**Completed**: [DATE]  
**Status**: TEMPLATE (fill after observation)

---

## Executive Summary

One paragraph: What happened during Stage 9 in production?

[SUMMARY]

**Overall verdict**: Success / Partial Success / Needs Revision / Failure

---

## What Worked

List 3-5 things that exceeded expectations or confirmed design.

### 1. [TITLE]

**What happened**:
- 

**Why it matters**:
- 

**Design validated**:
- 

---

### 2. [TITLE]

**What happened**:
- 

**Why it matters**:
- 

**Design validated**:
- 

---

### 3. [TITLE]

**What happened**:
- 

**Why it matters**:
- 

**Design validated**:
- 

---

## What Surprised You

List 3-5 things you didn't expect (good or bad).

### 1. [TITLE]

**Expected**:
- 

**Actually happened**:
- 

**Why the mismatch**:
- 

**Implications**:
- 

---

### 2. [TITLE]

**Expected**:
- 

**Actually happened**:
- 

**Why the mismatch**:
- 

**Implications**:
- 

---

### 3. [TITLE]

**Expected**:
- 

**Actually happened**:
- 

**Why the mismatch**:
- 

**Implications**:
- 

---

## What Assumptions Were Wrong

List design assumptions that reality contradicted.

### Assumption 1

**Assumed**:
- 

**Reality**:
- 

**Impact**:
- 

**Needs revision?** [YES/NO]

---

### Assumption 2

**Assumed**:
- 

**Reality**:
- 

**Impact**:
- 

**Needs revision?** [YES/NO]

---

### Assumption 3

**Assumed**:
- 

**Reality**:
- 

**Impact**:
- 

**Needs revision?** [YES/NO]

---

## Invariant Stress Test

Did any system invariants come under pressure?

### Invariant 1: Idempotency

**Violated?** [YES/NO]

**Evidence**:
- 

**Action needed**:
- 

---

### Invariant 2: Traceability

**Violated?** [YES/NO]

**Evidence**:
- 

**Action needed**:
- 

---

### Invariant 3: Auditability

**Violated?** [YES/NO]

**Evidence**:
- 

**Action needed**:
- 

---

### Invariant 4: Transparency

**Violated?** [YES/NO]

**Evidence**:
- 

**Action needed**:
- 

---

### Invariant 5: Reconstructibility

**Violated?** [YES/NO]

**Evidence**:
- 

**Action needed**:
- 

---

### Invariant 6: AI Subordination

**Violated?** [YES/NO]

**Evidence**:
- 

**Action needed**:
- 

---

## Authority Leakage Assessment

The critical question: Did AI ever feel like it was making decisions?

### User-Felt Authority Leakage

**Did you ever feel the AI was in control?** [YES/NO]

**Examples**:
- 

**Severity**: [LOW/MEDIUM/HIGH]

**Root cause**:
- 

---

### Design-Level Authority Leakage

**Did AI bypass human review structurally?** [YES/NO]

**Examples**:
- 

**Severity**: [LOW/MEDIUM/HIGH]

**Root cause**:
- 

---

### Subtle Authority Leakage

**Did framing or UI create implicit pressure?** [YES/NO]

**Examples**:
- 

**Severity**: [LOW/MEDIUM/HIGH]

**Root cause**:
- 

---

## Trust Calibration

How did trust evolve over the observation period?

### Initial Trust (Day 1)

**Level**: [1-10]

**Factors**:
- 

---

### Final Trust (Day [N])

**Level**: [1-10]

**Factors**:
- 

---

### Trust Direction

**Direction**: Increased / Decreased / Stable / Volatile

**Why**:
- 

**Key moments that shifted trust**:
1. 
2. 
3. 

---

## AI Suggestion Quality

### Quantitative

**Total suggestions**: [COUNT]  
**Approved**: [COUNT] ([PERCENTAGE]%)  
**Rejected**: [COUNT] ([PERCENTAGE]%)  
**Ignored**: [COUNT] ([PERCENTAGE]%)

**Confidence correlation**:
- High confidence (≥0.8): [PERCENTAGE]% approved
- Medium confidence (0.5-0.8): [PERCENTAGE]% approved
- Low confidence (<0.5): [PERCENTAGE]% approved

---

### Qualitative

**Best suggestion**:
- [TITLE]
- Why: [REASON]

**Worst suggestion**:
- [TITLE]
- Why: [REASON]

**Most surprising suggestion**:
- [TITLE]
- Why: [REASON]

---

## Rationale Effectiveness

### Usage Patterns

**Always read**: [PERCENTAGE]%  
**Sometimes read**: [PERCENTAGE]%  
**Never read**: [PERCENTAGE]%

**When rationales helped**:
- 

**When rationales were ignored**:
- 

**When rationales were annoying**:
- 

---

### Design Implications

**Rationale length**: Too long / Just right / Too short

**Rationale clarity**: Clear / Sometimes clear / Confusing

**Rationale value**: High / Medium / Low

**Changes needed**:
- 

---

## Failure Safety

### AI Failures Observed

**Total AI failures**: [COUNT]

**Types**:
- Timeout: [COUNT]
- Malformed output: [COUNT]
- API error: [COUNT]
- Other: [COUNT]

---

### Fallback Behavior

**Fallback triggered**: [COUNT] times

**User experience during fallback**:
- 

**Fallback quality vs AI quality**:
- 

**Design validated?** [YES/NO]

---

## Provider Performance

If multiple providers used:

### OpenAI

**Suggestions**: [COUNT]  
**Approval rate**: [PERCENTAGE]%  
**Avg confidence**: [NUMBER]  
**Failures**: [COUNT]

**Subjective quality**: [RATING]

---

### Anthropic

**Suggestions**: [COUNT]  
**Approval rate**: [PERCENTAGE]%  
**Avg confidence**: [NUMBER]  
**Failures**: [COUNT]

**Subjective quality**: [RATING]

---

### Provider Comparison

**Preferred**: [PROVIDER] because [REASON]

**Difference noticeable?** [YES/NO]

---

## User Behavior Patterns

What did you actually do (vs what you expected to do)?

### Approval Patterns

**Time to approve**: [FAST/MEDIUM/SLOW]

**Read before approve**: [ALWAYS/SOMETIMES/NEVER]

**Confidence threshold**: [NUMBER] (below which you were skeptical)

---

### Rejection Patterns

**Common rejection reasons**:
1. 
2. 
3. 

**Time to reject**: [FAST/MEDIUM/SLOW]

---

### Ignoring Patterns

**When did you ignore AI entirely?**
- 

**Why?**
- 

---

## Prompt Quality

### Prompt V1 Performance

**Effective**: [YES/NO]

**Problems observed**:
- 

**Improvements needed**:
- 

---

### Specific Examples

**Good prompt behavior**:
- Input: [TEXT]
- Output: [TITLE]
- Why good: [REASON]

**Bad prompt behavior**:
- Input: [TEXT]
- Output: [TITLE]
- Why bad: [REASON]

---

## Stage 10 Readiness Assessment

Based on observation, is Stage 10 warranted?

### Data Sufficiency

**Total AI suggestions**: [COUNT]  
**Minimum threshold**: 100

**Sufficient data?** [YES/NO]

**Usage duration**: [DAYS]  
**Minimum threshold**: 30 days

**Sufficient duration?** [YES/NO]

---

### Pattern Detection

**Patterns observed**:
1. [PATTERN]
2. [PATTERN]
3. [PATTERN]

**Patterns would be useful to surface?** [YES/NO]

**Why / Why not**:
- 

---

### User Interest

**Would you want insights about your patterns?** [YES/NO]

**What kind of insights?**
- 

**What would NOT be helpful?**
- 

---

### Risk Assessment

**Risk of prescriptive framing**: [LOW/MEDIUM/HIGH]

**Risk of authority leakage**: [LOW/MEDIUM/HIGH]

**Risk of compliance pressure**: [LOW/MEDIUM/HIGH]

**Overall risk**: [LOW/MEDIUM/HIGH]

---

## Stage 10 Decision Gate

### Option A: Proceed with Stage 10

**Rationale**:
- 

**Scope**:
- 

**Hypotheses to test**:
1. 
2. 
3. 

**Timeline**: [WEEKS]

---

### Option B: Narrow Stage 10 Scope

**Original scope too broad because**:
- 

**Revised scope**:
- 

**What to exclude**:
- 

---

### Option C: Pause Stage 10 Indefinitely

**Reasons**:
- 

**What needs to change first**:
- 

**Revisit when**:
- 

---

### Option D: Revise Stage 9 First

**Problems to fix**:
1. 
2. 
3. 

**Then reconsider Stage 10**: [YES/NO]

---

## Recommended Path Forward

**Decision**: [A / B / C / D]

**Reasoning** (3-5 sentences):


**Prerequisites before next stage**:
1. 
2. 
3. 

---

## Lessons for AI System Design

What did this teach you about building ethical AI?

### Lesson 1

**Principle**:
- 

**Evidence**:
- 

**Applicable elsewhere**: [YES/NO]

---

### Lesson 2

**Principle**:
- 

**Evidence**:
- 

**Applicable elsewhere**: [YES/NO]

---

### Lesson 3

**Principle**:
- 

**Evidence**:
- 

**Applicable elsewhere**: [YES/NO]

---

## Closing Reflection

One paragraph: What would you tell someone building a similar system?

[REFLECTION]

---

## Sign-Off

**Observation Complete**: [YES/NO]  
**Postmortem Complete**: [YES/NO]  
**Stage 10 Decision**: [PROCEED / NARROW / PAUSE / REVISE]  
**Next Action**: [SPECIFIC NEXT STEP]

**Completed by**: [NAME]  
**Date**: [DATE]

---

**This document closes Stage 9 observation and opens Stage 10 decision-making.**
