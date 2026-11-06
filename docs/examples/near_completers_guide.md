# Near-Completer Analysis Guide & Worked Example

> [!NOTE]
> **Synthetic Data Notice:** The underlying data in this repository is synthetic mock data from Achieving the Dream and the Postsecondary Data Partnership (PDP). Nothing built on it represents findings about real students or institutions.

This guide illustrates an end-to-end walkthrough using the **Metadata AI Assistant** to discover near-completers—students who stopped out within 15 credits of completing their certificate or degree.

---

## The Scenario

An academic advising director wants to re-engage stopped-out students who are close to graduating:

> **Advisor Prompt to Assistant:**  
> *"Our advising task force wants to re-engage students who were within one semester of finishing their credential but stopped enrolling. Which data view should we look at, and what institutional friction points should we check?"*

---

## The Assistant's Response

### 1. Recommended View & Datasets
- **View:** Near-Completer Stop-Out & Completion Bottleneck View
- **Datasets:**
  - Core PDP: [`student`](../../normalized-data-model/README.md#the-tables) and [`cohort_membership`](../../normalized-data-model/README.md#the-tables)
  - Supplementary: `degree_audit_catalog` and `registration_holds`
- **Target Measure:** Credential Completion Risk (Note: PDP `retention` strictly measures Year 1 to Year 2 return; near-completer stop-out is evaluated through degree audit and term enrollment).

### 2. Recommended Breakdowns
1. `degree_audit_catalog.credits_remaining` (bucketed: $\le 6$ credits, $7\text{--}15$ credits)
2. `degree_audit_catalog.program_code` (academic major / certificate track)
3. `student.student_age` (traditional vs. adult learners $> 24$)
4. `registration_holds.prevents_registration` (pre-aggregated to boolean hold indicator)

### 3. Why This View Was Chosen
Standard PDP files do not show how many credits count toward graduation. Connecting student records to a degree audit shows which students are 1-2 classes away from graduating (`credits_remaining <= 15`). Filtering by `is_primary_program = TRUE` avoids row multiplication for dual majors. Adding registration holds shows if unpaid balances (such as a $50 library fine) stopped them from enrolling.

### 4. Why Other Measures/Datasets Were Rejected
- **Raw PDP Credit Accumulation (`number_of_credits_earned_yr_1`):** Rejected because PDP credits count all classes, including remedial courses and general electives that do not satisfy degree requirements.
- **Entry Retention (`retention`):** Retention only covers return from Year 1 to Year 2; it cannot evaluate whether students stopping out in Year 3 or 4 return to finish their credential.

### 5. Small-Group Caution ($n < 10$)
> [!WARNING]
> Small departments or specific age groups may have fewer than 10 students. To protect student privacy, hide the count for any group with fewer than 10 students. If one group in a breakdown is suppressed, suppress a second group or omit totals (complementary suppression) so numbers cannot be calculated by subtraction.

### 6. Approved Local SQL Query

Run this query directly behind your institutional firewall in SQLite or PostgreSQL:

```sql
-- Approved Local Query: Near-completers with bursar hold indicator and n >= 10 suppression
WITH pre_aggregated_holds AS (
    SELECT
        student_id,
        MAX(CASE WHEN prevents_registration THEN 1 ELSE 0 END) AS has_blocking_hold,
        SUM(hold_amount) AS total_bursar_balance
    FROM registration_holds
    GROUP BY student_id
)
SELECT
    audit.program_code,
    s.student_age,
    CASE 
        WHEN audit.credits_remaining <= 6 THEN '1-2 courses (<= 6 credits)'
        ELSE '1 term (7-15 credits)'
    END AS proximity_bracket,
    COALESCE(h.has_blocking_hold, 0) AS has_registration_hold,
    COUNT(*) AS eligible_candidates
FROM student s
JOIN degree_audit_catalog audit 
    ON s.student_id = audit.student_id
LEFT JOIN pre_aggregated_holds h 
    ON s.student_id = h.student_id
WHERE audit.is_primary_program
  AND audit.credits_remaining <= 15
GROUP BY 
    audit.program_code,
    s.student_age,
    proximity_bracket,
    COALESCE(h.has_blocking_hold, 0)
HAVING COUNT(*) >= 10;  -- Institutional small-cell suppression
```

---

## How to Use `metadata_pack.json` in Any Chat Tool

The Metadata Assistant relies on a standalone JSON pack with zero database connections, allowing it to be used with conversational AI tools:

> [!CAUTION]
> **Data Governance Notice:** When `metadata_pack.json` is generated from a production campus database (instead of synthetic demo data), statistical fields (`null_share`, `distinct_count`, `row_count`) reflect real institutional numbers. Ensure your institutional privacy and FERPA officers approve before pasting generated packs into commercial cloud AI tools (ChatGPT, Gemini, or Claude). Always use synthetic data packs for public exploration.

1. **Generate the Pack:**
   ```bash
   python scripts/build_metadata_pack.py
   ```
2. **Open `metadata_pack.json`** (or `metadata_pack_additions.json`) in your editor and copy its contents.
3. **Set the System / Starter Prompt:**
   > *"You are the Metadata AI Assistant. You only have access to the attached `metadata_pack.json`. You have zero access to student-level data and must decline any request for student IDs, names, or individual records. Your role is to suggest views, measures, breakdowns, why_chosen/why_others_rejected rationale, small-group cautions ($n < 10$), complementary suppression guidance, and approved local SQL query templates."*
4. **Ask your exploratory question:** You will receive safe, private recommendations without exposing institutional student records.
