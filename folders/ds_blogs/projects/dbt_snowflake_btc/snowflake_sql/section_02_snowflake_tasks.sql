-- =====================================================================
-- Project: The Complete Snowflake & dbt Hands On Course
-- Section 2 — Snowflake Automation (Tasks)
-- Lecture 24: Introduction to Snowflake Tasks (scheduled task creation)
-- Author : Trinidad Cisneros
-- Goal   : Create a scheduled task that automatically refreshes the
--          WEATHER table from the weather_stage every night.
-- Where  : run from any Snowflake worksheet (browser UI).
-- =====================================================================
--
-- KEY CONCEPT — what a task is:
-- A task is a stored, named piece of SQL that Snowflake runs on a
-- schedule (or in response to a parent task finishing). Think of it
-- as a cron job that lives inside your database.
--
-- KEY CONCEPT — tasks are SUSPENDED at creation:
-- When you CREATE TASK, the task exists but does NOT run on schedule
-- until you explicitly say `ALTER TASK ... RESUME;`. That's a safety
-- feature so you don't accidentally schedule work before testing.
--
-- KEY CONCEPT — cron expressions:
-- The SCHEDULE clause uses a 5 field cron pattern:
--   minute  hour  day-of-month  month  day-of-week
-- '0 0 * * *' means: at minute 0, hour 0 (midnight), every day.
-- Crontab Guru (https://crontab.guru) is a great free tool to translate
-- between English and cron syntax.
--
-- COST FLAG — daily scheduled tasks cost real money:
-- A WEATHERTASK that runs once a day on COMPUTE_WH (X-Small) for
-- ~10-30 seconds uses ~0.01 credits per run × 30 days = ~0.3 credits
-- per month, which is ~$1/month on Enterprise. Small, but it adds up
-- if you forget tasks are running. Resume only when you want the
-- schedule to fire, and SUSPEND when you don't need it anymore.
-- =====================================================================


-- ---------------------------------------------------------------------
-- ACTION 1 — Set context (role, database, schema, warehouse)
-- Why:
--   - Tasks need to be created from a role with sufficient privileges;
--     ACCOUNTADMIN works fine for learning.
--   - DATABASE and SCHEMA set the default location so we don't have
--     to fully qualify every reference.
-- ---------------------------------------------------------------------
USE ROLE ACCOUNTADMIN;
USE DATABASE DEMO;
USE SCHEMA DEMO_SCHEMA;
USE WAREHOUSE COMPUTE_WH;


-- ---------------------------------------------------------------------
-- ACTION 2 — Create the WEATHERTASK scheduled task
-- Why:
--   - WAREHOUSE: which compute will run the task (X-Small to stay cheap).
--   - SCHEDULE: 'USING CRON 0 0 * * * UTC' = every day at midnight UTC.
--   - AS: the SQL the task runs each time it fires. Here it's a COPY
--     INTO that pulls JSON files from the weather_stage and writes the
--     parsed fields into the WEATHER table.
--   - The task is created SUSPENDED. It will NOT run on schedule until
--     you run ALTER TASK ... RESUME (covered in later lectures).
-- ---------------------------------------------------------------------
CREATE OR REPLACE TASK DEMO.DEMO_SCHEMA.WEATHERTASK
  WAREHOUSE = COMPUTE_WH
  SCHEDULE  = 'USING CRON 0 0 * * * UTC'
AS
  COPY INTO DEMO.DEMO_SCHEMA.WEATHER
  FROM (
    SELECT
      t.$1:city:findname,
      t.$1:city:coord:lat,
      t.$1:city:coord:lon,
      t.$1:clouds:all,
      t.$1:main:humidity,
      t.$1:main:pressure,
      t.$1:main:temp,
      t.$1:time,
      t.$1:weather[0]:main
    FROM @DEMO.DEMO_SCHEMA.weather_stage t
  );


-- ---------------------------------------------------------------------
-- ACTION 3 — Verify the task exists and is SUSPENDED
-- Why:
--   - SHOW TASKS lists every task in the current schema.
--   - Expected: 1 row, WEATHERTASK, state = SUSPENDED, schedule shown.
--   - If state shows STARTED, that means it's actively scheduled and
--     will run at midnight UTC tonight (and every night after).
-- ---------------------------------------------------------------------
SHOW TASKS IN SCHEMA DEMO.DEMO_SCHEMA;


-- =====================================================================
-- Lecture 25: Child task and DAG of tasks
-- =====================================================================
--
-- KEY CONCEPT — what a DAG is:
-- DAG stands for Directed Acyclic Graph. In plain language:
--   * "Directed"  → tasks have a clear order (parent → child)
--   * "Acyclic"   → no loops; task C can't trigger task A back
--   * "Graph"     → a chain (or tree) of tasks where each waits for
--                   its parent to finish before starting
-- Think of dominoes: WEATHERTASK falls (finishes) → BIKETASK falls
-- (runs) → if you added a third task, it would fall after BIKETASK.
--
-- KEY CONCEPT — root vs child task:
--   * Root task: has a SCHEDULE (the cron). Runs on its own clock.
--   * Child task: uses AFTER <parent_task>. No schedule of its own;
--                 fires only when the parent succeeds.
-- Only the root task in the DAG needs a SCHEDULE; children inherit
-- timing by being chained to it.
--
-- KEY CONCEPT — resuming a DAG:
-- You must RESUME the root task LAST. Children must be resumed BEFORE
-- the root, otherwise the root will run with no children attached.
-- (Daniel covers the exact order in lecture 26.)
-- =====================================================================


-- ---------------------------------------------------------------------
-- ACTION 4 — Create the BIKETASK as a child of WEATHERTASK
-- Why:
--   - WAREHOUSE: COMPUTE_WH (cheap X-Small).
--   - AFTER DEMO.DEMO_SCHEMA.WEATHERTASK: ties this task to the parent.
--     No SCHEDULE clause; it fires only after the parent succeeds.
--   - AS: the COPY INTO that loads the BIKE table from BIKE_STAGE
--     (using all 13 t.$N columns as STRINGs, same pattern as lecture 22).
--   - Fully qualified @DEMO.DEMO_SCHEMA.BIKE_STAGE (Daniel's resource
--     txt had a typo — @DEMO_SCHEMA.BIKE_STAGE without the database).
--   - Like WEATHERTASK, this task is created SUSPENDED.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TASK DEMO.DEMO_SCHEMA.BIKETASK
  WAREHOUSE = COMPUTE_WH
  AFTER DEMO.DEMO_SCHEMA.WEATHERTASK
AS
  COPY INTO DEMO.DEMO_SCHEMA.BIKE
  FROM (
    SELECT
      t.$1,
      t.$2,
      t.$3,
      t.$4,
      t.$5,
      t.$6,
      t.$7,
      t.$8,
      t.$9,
      t.$10,
      t.$11,
      t.$12,
      t.$13
    FROM @DEMO.DEMO_SCHEMA.BIKE_STAGE t
  );


-- ---------------------------------------------------------------------
-- ACTION 5 — Verify the DAG: both tasks exist, BIKETASK has predecessor
-- Why:
--   - SHOW TASKS lists every task in the schema.
--   - Expected: 2 rows.
--       * WEATHERTASK: state=suspended, predecessors=[], schedule shown.
--       * BIKETASK:    state=suspended, predecessors=[WEATHERTASK], no schedule.
--   - The predecessors column is what confirms the DAG link.
-- ---------------------------------------------------------------------
SHOW TASKS IN SCHEMA DEMO.DEMO_SCHEMA;


-- =====================================================================
-- Lecture 26: Task management — RESUME, SUSPEND, EXECUTE, TASK_HISTORY
-- =====================================================================
--
-- KEY CONCEPT — the three management verbs:
--   ALTER TASK ... RESUME   → activate the schedule (cron starts firing)
--   ALTER TASK ... SUSPEND  → deactivate the schedule (no more runs)
--   EXECUTE TASK ...        → one-time manual trigger (ignores schedule)
--
-- KEY CONCEPT — DAG resume order is BACKWARDS:
-- When resuming a DAG, you must resume CHILDREN BEFORE the root.
-- If you resume the root first, it has no active children to chain to
-- and the DAG won't behave as expected.
-- Correct order: BIKETASK RESUME → WEATHERTASK RESUME
-- (Daniel demonstrates this exact order in the lecture.)
--
-- KEY CONCEPT — TASK_HISTORY:
-- Snowflake records every task execution in a system view called
-- TASK_HISTORY. You query it like a function:
--   SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY());
-- This shows when each task ran, whether it succeeded or failed, how
-- it was scheduled (cron vs manual), the query ID, and more.
--
-- COST FLAGS for this lecture:
--   ALTER TASK ... RESUME    → no immediate cost; sets the cron live so
--                              tasks fire at every scheduled time
--                              (~$1/month if both stay resumed)
--   EXECUTE TASK ...         → runs the SQL ONCE right now; charges
--                              compute for that execution
--                              (~$0.01 for WEATHERTASK; ~$0.15 for
--                              BIKETASK because BIKE_STAGE is 35M rows)
--   SHOW TASKS / TASK_HISTORY → metadata only, free, safe to run
-- =====================================================================


-- ---------------------------------------------------------------------
-- ACTION 6 — Resume the tasks (DO NOT RUN unless you want the schedule active)
-- Why this order:
--   Children before parents: BIKETASK first, then WEATHERTASK.
--   If you flip the order, the schedule could fire on WEATHERTASK
--   before BIKETASK is ready to receive the chain.
-- Trinidad's stance:
--   You said you want to keep these suspended for cost reasons.
--   These two lines are documented here for reference only — leave
--   them commented out so they don't run accidentally.
-- ---------------------------------------------------------------------
-- ALTER TASK DEMO.DEMO_SCHEMA.BIKETASK    RESUME;
-- ALTER TASK DEMO.DEMO_SCHEMA.WEATHERTASK RESUME;


-- ---------------------------------------------------------------------
-- ACTION 7 — Manually trigger a task with EXECUTE (also DO NOT RUN by default)
-- Why this might be useful:
--   Lets you test the SQL without waiting until midnight.
--   When you execute the parent (root), the whole DAG runs in order.
-- Cost reminder:
--   Running WEATHERTASK manually costs about $0.01.
--   Running BIKETASK manually costs about $0.15 (35M rows COPY).
--   The DAG chain runs BOTH back to back, so total ≈ $0.16 per execute.
-- Leave commented out to avoid the charge.
-- ---------------------------------------------------------------------
-- EXECUTE TASK DEMO.DEMO_SCHEMA.WEATHERTASK;


-- ---------------------------------------------------------------------
-- ACTION 8 — Inspect run history with TASK_HISTORY (SAFE, free to run)
-- Why:
--   Shows every task execution (or upcoming scheduled execution).
--   Columns include: NAME, STATE (SCHEDULED / SUCCEEDED / FAILED),
--   SCHEDULED_TIME, QUERY_START_TIME, RETURN_VALUE, ERROR_MESSAGE.
--   Even with no manual or scheduled runs yet, this may return rows
--   for upcoming scheduled executions (state = SCHEDULED) if tasks
--   are ever resumed.
-- ---------------------------------------------------------------------
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
ORDER BY SCHEDULED_TIME;


-- ---------------------------------------------------------------------
-- ACTION 9 — Final safety check: confirm tasks are SUSPENDED before closing
-- Why:
--   If you ever accidentally ran the RESUME lines above, this is your
--   chance to put them back to safe state.
--   Running SUSPEND on an already-suspended task throws a harmless
--   "cannot be suspended" error — same pattern as warehouse suspend.
-- ---------------------------------------------------------------------
ALTER TASK DEMO.DEMO_SCHEMA.BIKETASK    SUSPEND;
ALTER TASK DEMO.DEMO_SCHEMA.WEATHERTASK SUSPEND;

SHOW TASKS IN SCHEMA DEMO.DEMO_SCHEMA;


-- =====================================================================
-- END OF SECTION 2
-- Next: Section 3 (DBT) — where the real transformation work starts.
-- =====================================================================
