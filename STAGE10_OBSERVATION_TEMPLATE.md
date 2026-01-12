# Stage 10: Production Observation Template
## Data Collection Framework for Insight Hypothesis Generation

**Purpose**: Collect structured observations from Stage 9 production usage to inform Stage 10 design.

**Timeline**: Minimum 1 month of production usage  
**Started**: [DATE]  
**Target Completion**: [DATE + 30 days]  
**Status**: NOT STARTED (awaiting Stage 9 deployment)

---

## Observation Period Requirements

Before Stage 10 implementation may proceed, collect:

- ✅ ≥100 AI suggestions generated
- ✅ ≥1 month of continuous system usage
- ✅ ≥30 human review decisions (approve/reject)
- ✅ Mix of AI-generated and manual task candidates
- ✅ At least 2 different users (if multi-user) or 30+ days single-user

---

## Data Collection Queries

### 1. AI Suggestion Volume

```sql
-- How many AI suggestions have been generated?
SELECT 
  provider,
  COUNT(*) as suggestion_count,
  MIN(created_at) as first_suggestion,
  MAX(created_at) as latest_suggestion
FROM ai_suggestions
GROUP BY provider;
```

**Observations**:
- Total suggestions: [NUMBER]
- Date range: [START] to [END]
- Providers used: [LIST]

### 2. Human Decision Patterns

```sql
-- What percentage of AI suggestions are approved vs rejected?
SELECT 
  ra.action,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage
FROM review_actions ra
JOIN task_candidates tc ON ra.candidate_id = tc.id
WHERE tc.ai_suggestion_id IS NOT NULL
GROUP BY ra.action;
```

**Observations**:
- Approval rate: [PERCENTAGE]%
- Rejection rate: [PERCENTAGE]%
- Notable patterns: [DESCRIPTION]

### 3. Confidence vs Approval Correlation

```sql
-- Does AI confidence correlate with human approval?
SELECT 
  CASE 
    WHEN (ais.suggestion_json->>'confidence')::float < 0.5 THEN 'Low (< 0.5)'
    WHEN (ais.suggestion_json->>'confidence')::float < 0.8 THEN 'Medium (0.5-0.8)'
    ELSE 'High (≥ 0.8)'
  END as confidence_bracket,
  ra.action,
  COUNT(*) as count
FROM ai_suggestions ais
JOIN task_candidates tc ON tc.ai_suggestion_id = ais.id
JOIN review_actions ra ON ra.candidate_id = tc.id
GROUP BY confidence_bracket, ra.action
ORDER BY confidence_bracket, ra.action;
```

**Observations**:
- High confidence approval rate: [PERCENTAGE]%
- Low confidence approval rate: [PERCENTAGE]%
- Correlation exists: [YES/NO]

### 4. Priority Distribution

```sql
-- What priority levels do AI and humans assign?
SELECT 
  tc.priority,
  CASE WHEN tc.ai_suggestion_id IS NULL THEN 'Manual' ELSE 'AI' END as source,
  COUNT(*) as count
FROM task_candidates tc
GROUP BY tc.priority, source
ORDER BY priority, source;
```

**Observations**:
- AI priority distribution: [DESCRIBE]
- Human priority distribution: [DESCRIBE]
- Differences noted: [DESCRIBE]

### 5. Task Completion Patterns

```sql
-- Do AI-suggested tasks get completed at different rates?
SELECT 
  CASE WHEN t.raw_event_id IN (
    SELECT raw_event_id FROM task_candidates WHERE ai_suggestion_id IS NOT NULL
  ) THEN 'AI-originated' ELSE 'Manual' END as source,
  t.status,
  COUNT(*) as count,
  ROUND(AVG(EXTRACT(EPOCH FROM (COALESCE(t.completed_at, NOW()) - t.created_at)) / 86400), 1) as avg_days_to_complete
FROM tasks t
GROUP BY source, t.status
ORDER BY source, t.status;
```

**Observations**:
- AI task completion rate: [PERCENTAGE]%
- Manual task completion rate: [PERCENTAGE]%
- Time-to-completion difference: [DAYS]

### 6. Temporal Patterns

```sql
-- When do users approve/reject tasks?
SELECT 
  EXTRACT(HOUR FROM ra.timestamp) as hour_of_day,
  ra.action,
  COUNT(*) as count
FROM review_actions ra
GROUP BY hour_of_day, ra.action
ORDER BY hour_of_day;
```

**Observations**:
- Peak review hours: [HOURS]
- Approval patterns by time: [DESCRIBE]
- Rejection patterns by time: [DESCRIBE]

### 7. Provider Performance

```sql
-- Do different AI providers perform differently?
SELECT 
  ais.provider,
  ais.model,
  COUNT(*) as suggestions,
  SUM(CASE WHEN ra.action = 'approved' THEN 1 ELSE 0 END) as approved,
  ROUND(100.0 * SUM(CASE WHEN ra.action = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 1) as approval_rate,
  ROUND(AVG((ais.suggestion_json->>'confidence')::float), 2) as avg_confidence
FROM ai_suggestions ais
JOIN task_candidates tc ON tc.ai_suggestion_id = ais.id
JOIN review_actions ra ON ra.candidate_id = tc.id
GROUP BY ais.provider, ais.model
ORDER BY approval_rate DESC;
```

**Observations**:
- Best performing provider: [NAME] ([APPROVAL_RATE]%)
- Confidence calibration: [WELL/POORLY calibrated]
- Model differences: [DESCRIBE]

---

## Qualitative Observations

### User Feedback

**Question 1**: Do AI suggestions feel helpful or intrusive?
- Response: [USER FEEDBACK]

**Question 2**: Are rationales clear and useful?
- Response: [USER FEEDBACK]

**Question 3**: What patterns have you noticed in your own approval/rejection behavior?
- Response: [USER FEEDBACK]

**Question 4**: Would you want insights about your task patterns?
- Response: [USER FEEDBACK]

**Question 5**: What would make you trust AI suggestions more?
- Response: [USER FEEDBACK]

### System Behavior Notes

**Unexpected Behaviors**:
- [OBSERVATION 1]
- [OBSERVATION 2]
- [OBSERVATION 3]

**Edge Cases Encountered**:
- [EDGE CASE 1]
- [EDGE CASE 2]

**False Positives** (AI suggested, human rejected):
- Common themes: [DESCRIBE]
- Examples: [LIST]

**False Negatives** (AI should have suggested, didn't):
- Examples: [LIST]

---

## Insight Hypothesis Generation

Based on observations, potential Stage 10 insights:

### Hypothesis 1: [NAME]

**Pattern Observed**: [DESCRIBE PATTERN]  
**Data Supporting**: [QUERY RESULTS]  
**Potential Insight**: "You [PATTERN DESCRIPTION]"  
**Value to User**: [WHY THIS MATTERS]  
**Prescriptive Risk**: [LOW/MEDIUM/HIGH]  

### Hypothesis 2: [NAME]

**Pattern Observed**: [DESCRIBE PATTERN]  
**Data Supporting**: [QUERY RESULTS]  
**Potential Insight**: "You [PATTERN DESCRIPTION]"  
**Value to User**: [WHY THIS MATTERS]  
**Prescriptive Risk**: [LOW/MEDIUM/HIGH]  

### Hypothesis 3: [NAME]

**Pattern Observed**: [DESCRIBE PATTERN]  
**Data Supporting**: [QUERY RESULTS]  
**Potential Insight**: "You [PATTERN DESCRIPTION]"  
**Value to User**: [WHY THIS MATTERS]  
**Prescriptive Risk**: [LOW/MEDIUM/HIGH]  

---

## Rejected Hypotheses

Track insights that were considered but rejected:

### Rejected 1: [NAME]

**Why Rejected**: [REASON]  
**Violates Invariant**: [WHICH ONE]  
**Risk**: [DESCRIBE RISK]  

---

## Semantic Memory Feasibility Assessment

### Embedding Strategy

**Text Sources for Embeddings**:
- [ ] Task titles
- [ ] Task descriptions
- [ ] AI rationales
- [ ] Raw event payloads (redacted)

**Embedding Model Candidates**:
- Option 1: OpenAI text-embedding-3-small (1536 dimensions)
- Option 2: Sentence-transformers/all-MiniLM-L6-v2 (384 dimensions, local)
- Option 3: [OTHER]

**Selected**: [MODEL] because [REASON]

### Clustering Strategy

**Clustering Algorithm**:
- [ ] K-means (requires k selection)
- [ ] HDBSCAN (automatic cluster detection)
- [ ] Agglomerative hierarchical

**Selected**: [ALGORITHM] because [REASON]

**Estimated Cluster Count**: [NUMBER] based on [REASONING]

### Similarity Search Use Cases

**Potential Use Cases** (all must remain descriptive):
1. "Tasks similar to this one"
2. "Recurring themes in your work"
3. "Tasks you completed quickly vs slowly"

**Rejected Use Cases** (too prescriptive):
1. ❌ "Recommend similar tasks to approve"
2. ❌ "Tasks you should prioritize"
3. ❌ "Predict task completion time"

---

## Implementation Readiness Checklist

Before proceeding to Stage 10 implementation:

### Data Requirements
- [ ] ≥100 AI suggestions collected
- [ ] ≥30 days of usage data
- [ ] ≥30 human review decisions
- [ ] At least 3 insight hypotheses validated

### Technical Requirements
- [ ] Read-only database user created
- [ ] Semantic schema designed (separate from operational)
- [ ] Embedding pipeline tested offline
- [ ] UI mockup for insights section created

### Ethical Requirements
- [ ] STAGE10_ETHICS_AND_INVARIANTS.md reviewed
- [ ] User consent mechanism designed
- [ ] Dismissibility feature specified
- [ ] No authority leakage confirmed

### User Requirements
- [ ] User expressed interest in insights
- [ ] User understands insights are descriptive only
- [ ] User has option to disable Stage 10

---

## Sign-Off

**Observation Period Completed**: [DATE]  
**Data Sufficient**: [YES/NO]  
**Insights Hypotheses**: [COUNT] validated  
**Ready for Stage 10 Implementation**: [YES/NO]  

**If NO, why not**:
- [REASON 1]
- [REASON 2]

**Next Actions**:
1. [ACTION 1]
2. [ACTION 2]

---

## Notes & Context

Use this section for freeform observations that don't fit above categories:

- [NOTE 1]
- [NOTE 2]
- [NOTE 3]
