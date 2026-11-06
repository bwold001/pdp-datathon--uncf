"""One file per measure. Each file has the same two parts, and run_measures.py calls them:

    NOTE                                the sentence that says who was counted
    count(connection, cohorts, groups)  return Counts for every (cohort, group)

Retention and persistence count in SQL with sql_counts.py. A measure can count in Python instead.
"""
