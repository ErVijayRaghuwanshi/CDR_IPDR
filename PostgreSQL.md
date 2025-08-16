Alright — here’s a **PostgreSQL schema** that creates your existing `targets` and `rules` tables, plus the new **`target_groups`**, **`target_group_targets`**, and **`target_group_rules`** tables, with proper relationships.

I’ll make sure to:

* Use **primary keys** and **foreign keys** for integrity.
* Allow **JSONB** for `custom_params` so you can store flexible rule configs.
* Support **same rule multiple times** in a group with different params.

---

```sql
-- ====================================
-- 1. Existing Tables
-- ====================================

CREATE TABLE targets (
    target_id VARCHAR(20) PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL,
    identifier VARCHAR(100) NOT NULL,
    associated_imsi VARCHAR(20),
    associated_imei VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    associated_bts VARCHAR(50),
    description TEXT
);

CREATE TABLE rules (
    rule_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version VARCHAR(20),
    rule_type VARCHAR(50),
    data_source VARCHAR(50),
    required_fields TEXT[] NOT NULL,
    default_params JSONB,
    tags TEXT[],
    sql_template TEXT
);

-- ====================================
-- 2. New Target Groups Table
-- ====================================

CREATE TABLE target_groups (
    group_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    status VARCHAR(20) NOT NULL
);

-- ====================================
-- 3. Mapping Table: Target Groups ↔ Targets
-- Many-to-many relationship
-- ====================================

CREATE TABLE target_group_targets (
    group_id VARCHAR(20) NOT NULL,
    target_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (group_id, target_id),
    FOREIGN KEY (group_id) REFERENCES target_groups (group_id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES targets (target_id) ON DELETE CASCADE
);

-- ====================================
-- 4. Mapping Table: Target Groups ↔ Rules
-- Allows same rule multiple times with different params
-- ====================================

CREATE TABLE target_group_rules (
    group_rule_id SERIAL PRIMARY KEY,
    group_id VARCHAR(20) NOT NULL,
    rule_id VARCHAR(20) NOT NULL,
    custom_params JSONB,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES target_groups (group_id) ON DELETE CASCADE,
    FOREIGN KEY (rule_id) REFERENCES rules (rule_id) ON DELETE CASCADE
);

-- Optional: Index for faster rule lookup
CREATE INDEX idx_target_group_rules_group ON target_group_rules (group_id);
CREATE INDEX idx_target_group_rules_rule ON target_group_rules (rule_id);
```

---

### 🔹 How relationships work:

* `target_group_targets` = **many-to-many** between `target_groups` and `targets`.
* `target_group_rules` = **many-to-many** between `target_groups` and `rules`, but with an **extra column** `custom_params` to store different configs for the same rule.
* `ON DELETE CASCADE` ensures that if you delete a group, its target mappings and rules get deleted automatically.

---

Do you want me to also **preload these tables with your sample data** so you can test joins immediately? That would give you ready-to-run `INSERT` statements.





Here’s the **PostgreSQL INSERT script** for your 10 targets, matching the table structure we created earlier:

```sql
INSERT INTO targets (
    target_id, target_type, identifier, associated_imsi, associated_imei,
    created_at, status, associated_bts, description
) VALUES
('TGT001', 'MOBILE_NUMBER', '9876543210', '405874321012345', '359123450123456',
 '2025-08-09T00:00:00Z', 'active', 'BTS001', 'Suspect mobile number under surveillance'),

('TGT002', 'IMEI', '359123450123457', '405874321012346', '359123450123457',
 '2025-08-09T00:00:00Z', 'active', 'BTS002', 'IMEI linked to multiple SIMs'),

('TGT003', 'IP_ADDRESS', '192.168.1.101', NULL, NULL,
 '2025-08-09T00:00:00Z', 'inactive', NULL, 'Suspect public IP from proxy logs'),

('TGT004', 'IMEI', '359123450123458', '405874321012347', '359123450123458',
 '2025-08-09T00:00:00Z', 'active', 'BTS003', 'IMEI suspected in device spoofing'),

('TGT005', 'MOBILE_NUMBER', '8765432109', '405874321012348', '359123450123459',
 '2025-08-09T00:00:00Z', 'active', 'BTS004', 'Known associate of suspect'),

('TGT006', 'IP_ADDRESS', '10.0.0.54', NULL, NULL,
 '2025-08-09T00:00:00Z', 'active', NULL, 'Internal IP triggering unusual activity'),

('TGT007', 'IMEI', '359123450123460', '405874321012349', '359123450123460',
 '2025-08-09T00:00:00Z', 'active', 'BTS005', 'Potential stolen device'),

('TGT008', 'MOBILE_NUMBER', '9988776655', '405874321012350', '359123450123461',
 '2025-08-09T00:00:00Z', 'active', 'BTS006', 'Burner phone activity'),

('TGT009', 'MOBILE_NUMBER', '9090909090', '405874321012351', '359123450123462',
 '2025-08-09T00:00:00Z', 'active', 'BTS007', 'SIM linked to VOIP calls'),

('TGT010', 'IP_ADDRESS', '172.16.24.89', NULL, NULL,
 '2025-08-09T00:00:00Z', 'inactive', NULL, 'Outbound suspicious traffic');
```

---

If you want, I can now prepare the **INSERT statements for your rules table** so the relationships can be tested with `target_groups`.
That way we’ll be able to join `target_group_rules` with actual rule data and see the `custom_params` in action.








Ah, I see the problem — in PostgreSQL you can’t just put an array or JSON literal inside single quotes as a plain string for `TEXT[]` or `JSONB` columns.
You have to use:

* `ARRAY[...]` syntax for arrays (`TEXT[]` columns).
* `'{"key": "value"}'::jsonb` for JSONB columns.

Your current `INSERT` fails because PostgreSQL thinks `'["MOBILENUMBER", "B_MOBILENUMBER"]'` is just a string, not an array or JSON, and the commas aren’t parsed properly.

---

Here’s the **fixed** version for your `rules` insert:

```sql
INSERT INTO rules (
    rule_id, name, description, created_at, modified_at, version, rule_type, data_source,
    required_fields, default_params, tags, sql_template
) VALUES
('R001', 'High-Frequency Communication Between Two Parties',
 'Detects unusually frequent calls or messages between two numbers within a short time window.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'CDR',
 ARRAY['MOBILENUMBER', 'B_MOBILENUMBER', 'TRANSACTIONSTARTTIME'],
 '{"FREQUENCY_THRESHOLD": 50, "TIME_WINDOW_HOURS": 24}'::jsonb,
 ARRAY['communication-pattern', 'coordination'],
 'SELECT MOBILENUMBER, B_MOBILENUMBER, COUNT(*) AS TOTAL_CALLS FROM cdr WHERE TRANSACTIONSTARTTIME >= TIMESTAMPADD(HOUR, -$TIME_WINDOW_HOURS, CURRENT_TIMESTAMP) GROUP BY MOBILENUMBER, B_MOBILENUMBER HAVING TOTAL_CALLS > $FREQUENCY_THRESHOLD'),

('R002', 'Unusual Call Duration',
 'Detects abnormally long or short calls.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'CDR',
 ARRAY['MOBILENUMBER', 'B_MOBILENUMBER', 'DURATION'],
 '{"MIN_DURATION_SEC": 3, "MAX_DURATION_SEC": 1200}'::jsonb,
 ARRAY['anomaly-duration', 'covert-communication'],
 'SELECT MOBILENUMBER, B_MOBILENUMBER, DURATION FROM cdr WHERE DURATION < $MIN_DURATION_SEC OR DURATION > $MAX_DURATION_SEC'),

('R003', 'Communication With Known Blacklisted Numbers',
 'Flags calls or messages to/from numbers on a watchlist.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'CDR',
 ARRAY['MOBILENUMBER', 'B_MOBILENUMBER'],
 '{"WATCHLIST_TABLE": "(9755491130, 9977315472)"}'::jsonb,
 ARRAY['watchlist', 'blacklisted'],
 'SELECT c.MOBILENUMBER, c.B_MOBILENUMBER, w.WATCHLIST_ID AS MATCHED_WATCHLIST_ID FROM cdr c JOIN $WATCHLIST_TABLE w ON c.MOBILENUMBER = w.NUMBER OR c.B_MOBILENUMBER = w.NUMBER'),

('R004', 'Frequent Cell Tower Location Changes',
 'Detects rapid movement across large distances.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'CDR',
 ARRAY['MOBILENUMBER', 'BTS', 'TRANSACTIONSTARTTIME'],
 '{"LOCATION_CHANGE_THRESHOLD": 5, "TIME_WINDOW_HOURS": 1}'::jsonb,
 ARRAY['mobility-pattern', 'evasion'],
 'SELECT MOBILENUMBER, COUNT(DISTINCT BTS) AS TOTAL_BTS_CHANGES FROM cdr WHERE TRANSACTIONSTARTTIME >= TIMESTAMPADD(HOUR, -$TIME_WINDOW_HOURS, CURRENT_TIMESTAMP) GROUP BY MOBILENUMBER HAVING TOTAL_BTS_CHANGES > $LOCATION_CHANGE_THRESHOLD'),

('R005', 'SIM Swap Detection',
 'Detects multiple IMEIs for same mobile number in a short time window, indicating a potential SIM swap.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'CDR',
 ARRAY['MOBILENUMBER', 'IMEI', 'TRANSACTIONSTARTTIME'],
 '{"IMEI_CHANGE_THRESHOLD": 2, "TIME_WINDOW_HOURS": 24}'::jsonb,
 ARRAY['fraud', 'identity-change', 'device'],
 'SELECT MOBILENUMBER, COUNT(DISTINCT IMEI) AS CHANGE_COUNT FROM cdr WHERE TRANSACTIONSTARTTIME >= TIMESTAMPADD(HOUR, -$TIME_WINDOW_HOURS, CURRENT_TIMESTAMP) GROUP BY MOBILENUMBER HAVING CHANGE_COUNT > $IMEI_CHANGE_THRESHOLD'),

('R006', 'High Volume of International Calls',
 'Flags unusual spikes in calls to foreign destinations, often used for organized crime.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'CDR',
 ARRAY['MOBILENUMBER', 'DSTCOUNTRY', 'TRANSACTIONSTARTTIME'],
 '{"FOREIGN_CALL_THRESHOLD": 10, "TIME_WINDOW_HOURS": 24}'::jsonb,
 ARRAY['international-traffic', 'anomaly', 'communication'],
 'SELECT MOBILENUMBER, DSTCOUNTRY, COUNT(*) AS TOTAL_FOREIGN_CALLS FROM cdr WHERE DSTCOUNTRY <> ''LOCAL'' AND TRANSACTIONSTARTTIME >= TIMESTAMPADD(HOUR, -$TIME_WINDOW_HOURS, CURRENT_TIMESTAMP) GROUP BY MOBILENUMBER, DSTCOUNTRY HAVING TOTAL_FOREIGN_CALLS > $FOREIGN_CALL_THRESHOLD'),

('R007', 'Access to Restricted Online Services',
 'Detects access to restricted or illegal domains/apps from the IPDR data.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'IPDR',
 ARRAY['MOBILENUMBER', 'DOMAIN', 'APPCATEGORY'],
 '{"RESTRICTED_TABLE": "restricted_list"}'::jsonb,
 ARRAY['content-monitoring', 'illegal-services', 'ip'],
 'SELECT i.MOBILENUMBER, i.DOMAIN, i.APPCATEGORY FROM ipdr i JOIN $RESTRICTED_TABLE r ON i.DOMAIN = r.DOMAIN OR i.APPCATEGORY = r.APPCATEGORY'),

('R008', 'Multiple Devices Using Same IP',
 'Detects when multiple unique IMEIs use the same IP address in a short time, indicating a potential hotspot or shared connection for coordinated activity.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'IPDR',
 ARRAY['SERVERIP', 'IMEI', 'TRANSACTIONSTARTTIME'],
 '{"DEVICE_COUNT_THRESHOLD": 3, "TIME_WINDOW_HOURS": 1}'::jsonb,
 ARRAY['coordination', 'hotspot', 'ip', 'device'],
 'SELECT SERVERIP, COUNT(DISTINCT IMEI) AS DEVICE_COUNT FROM ipdr WHERE TRANSACTIONSTARTTIME >= TIMESTAMPADD(HOUR, -$TIME_WINDOW_HOURS, CURRENT_TIMESTAMP) GROUP BY SERVERIP HAVING DEVICE_COUNT > $DEVICE_COUNT_THRESHOLD'),

('R009', 'Suspicious VoIP Traffic',
 'Detects encrypted or obfuscated VoIP calls outside of normal business hours, which may indicate covert communication.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'IPDR',
 ARRAY['MOBILENUMBER', 'APPLICATION', 'TRANSACTIONSTARTTIME'],
 '{"ALLOWED_HOURS_START": 8, "ALLOWED_HOURS_END": 22}'::jsonb,
 ARRAY['voip', 'covert', 'communication'],
 'SELECT MOBILENUMBER, APPLICATION FROM ipdr WHERE APPLICATION = ''VoIP'' AND (HOUR(TRANSACTIONSTARTTIME) < $ALLOWED_HOURS_START OR HOUR(TRANSACTIONSTARTTIME) > $ALLOWED_HOURS_END)'),

('R010', 'Repeated Contact With Foreign IP Addresses',
 'Flags repeated communications with the same foreign server IP, which could signal a command-and-control connection.',
 '2025-08-09T00:00:00Z', '2025-08-09T00:00:00Z', '1.0', 'Rule', 'IPDR',
 ARRAY['MOBILENUMBER', 'SERVERIP', 'DSTCOUNTRY'],
 '{"REPEAT_CONTACT_THRESHOLD": 20, "TIME_WINDOW_DAYS": 7}'::jsonb,
 ARRAY['foreign-connection', 'anomaly', 'ip'],
 'SELECT MOBILENUMBER, SERVERIP, DSTCOUNTRY FROM ipdr WHERE DSTCOUNTRY <> ''LOCAL'' AND TRANSACTIONSTARTTIME >= DATEADD(DAY, -$TIME_WINDOW_DAYS, CURRENT_DATE) GROUP BY MOBILENUMBER, SERVERIP, DSTCOUNTRY HAVING COUNT(*) > $REPEAT_CONTACT_THRESHOLD');
```

---

**Key changes**

* `ARRAY[...]` instead of `'[...]'` for `TEXT[]` fields.
* `'{"key": "value"}'::jsonb` instead of `'{"key": "value"}'` for JSONB fields.
* Proper double-single-quote escaping (`''LOCAL''`) inside SQL templates.

---

Do you want me to also give you a **batch insert for sample `target_groups`** and relationships so you can immediately test joins? That way you’ll have a complete working dataset.






Got it ✅
I’ll make **two sample target groups** and link them to your existing targets and rules so you can test relationships.

Here’s the PostgreSQL script:

```sql
-- 1. Insert target groups
INSERT INTO target_groups (
    group_id, name, description, created_at, status
) VALUES
('GRP001', 'Urban Surveillance Group',
 'High-priority surveillance of suspected individuals in urban areas',
 '2025-08-09T00:00:00Z', 'active'),

('GRP002', 'Cyber Activity Watch',
 'Monitoring of IP-based suspicious activity and coordinated device usage',
 '2025-08-09T00:00:00Z', 'active');


-- 2. Link 4 targets to each group
INSERT INTO target_group_targets (group_id, target_id) VALUES
-- GRP001 (Urban Surveillance)
('GRP001', 'TGT001'),
('GRP001', 'TGT002'),
('GRP001', 'TGT005'),
('GRP001', 'TGT009'),

-- GRP002 (Cyber Activity Watch)
('GRP002', 'TGT003'),
('GRP002', 'TGT006'),
('GRP002', 'TGT008'),
('GRP002', 'TGT010');

-- 3. Link 8 rules to each group (some overlap is fine)
INSERT INTO target_group_rules (group_id, rule_id, custom_params) VALUES
-- GRP001 Rules
('GRP001', 'R001', '{"FREQUENCY_THRESHOLD": 40}'::jsonb),
('GRP001', 'R002', '{"MAX_DURATION_SEC": 1500}'::jsonb),
('GRP001', 'R003', '{}'::jsonb),
('GRP001', 'R004', '{"LOCATION_CHANGE_THRESHOLD": 4}'::jsonb),
('GRP001', 'R005', '{}'::jsonb),
('GRP001', 'R006', '{"FOREIGN_CALL_THRESHOLD": 8}'::jsonb),
('GRP001', 'R009', '{"ALLOWED_HOURS_START": 6, "ALLOWED_HOURS_END": 20}'::jsonb),
('GRP001', 'R010', '{}'::jsonb),

-- GRP002 Rules
('GRP002', 'R003', '{}'::jsonb),
('GRP002', 'R004', '{}'::jsonb),
('GRP002', 'R006', '{}'::jsonb),
('GRP002', 'R007', '{}'::jsonb),
('GRP002', 'R008', '{"DEVICE_COUNT_THRESHOLD": 4}'::jsonb),
('GRP002', 'R009', '{}'::jsonb),
('GRP002', 'R010', '{"REPEAT_CONTACT_THRESHOLD": 15}'::jsonb),
('GRP002', 'R001', '{}'::jsonb);
```

---

**What this does**

* Creates **GRP001** and **GRP002** in `target_groups`.
* Associates **4 targets each** via `target_group_targets`.
* Links **8 rules each** with some custom parameter overrides in `target_group_rules`.

This means you can now run queries like:

```sql
SELECT g.name AS group_name, t.identifier AS target, r.name AS rule, gr.custom_params
FROM target_groups g
JOIN target_group_targets gt ON g.group_id = gt.group_id
JOIN targets t ON gt.target_id = t.target_id
JOIN target_group_rules gr ON g.group_id = gr.group_id
JOIN rules r ON gr.rule_id = r.rule_id
WHERE g.group_id = 'GRP001';
```

That will show you **every target in a group along with its active rules**.

---

Do you want me to also give you a **CDR/IPDR mock dataset** so these rules can be tested immediately in PostgreSQL? That way you can actually see matches.








You’re probably getting nothing because the joins require linked rows. Let’s 1) verify the data is present, then 2) use a JSON query that returns a group even if it has no targets/rules yet.

### 1) Quick sanity checks

```sql
-- does the group exist?
SELECT * FROM target_groups WHERE group_id = 'GRP001';

-- do mappings exist?
SELECT COUNT(*) AS target_links FROM target_group_targets WHERE group_id = 'GRP001';
SELECT COUNT(*) AS rule_links   FROM target_group_rules   WHERE group_id = 'GRP001';
```

### 2) Single group → one JSON object (never empty due to subqueries)

```sql
SELECT
  jsonb_build_object(
    'group_id',   g.group_id,
    'group_name', g.name,
    'status',     g.status,
    'targets',
      COALESCE((
        SELECT jsonb_agg(
                 jsonb_build_object(
                   'target_id',   t.target_id,
                   'target_type', t.target_type,
                   'identifier',  t.identifier
                 )
                 ORDER BY t.target_id
               )
        FROM target_group_targets gt
        JOIN targets t ON t.target_id = gt.target_id
        WHERE gt.group_id = g.group_id
      ), '[]'::jsonb),
    'rules',
      COALESCE((
        SELECT jsonb_agg(
                 jsonb_build_object(
                   'group_rule_id', gr.group_rule_id,
                   'rule_id',       r.rule_id,
                   'rule_type',     r.rule_type,
                   'name',          r.name,
                   'data_source',   r.data_source,
                   'description',   r.description,
                   'required_fields', r.required_fields,
                   'sql_template',  r.sql_template,
                   'custom_params', gr.custom_params
                 )
                 ORDER BY r.rule_id, gr.group_rule_id
               )
        FROM target_group_rules gr
        JOIN rules r ON r.rule_id = gr.rule_id
        WHERE gr.group_id = g.group_id
      ), '[]'::jsonb)
  ) AS group_data
FROM target_groups g
WHERE g.group_id = 'GRP001';
```

### 3) All groups keyed by `group_id` → `{ "GRP001": {...}, "GRP002": {...} }`

```sql
SELECT jsonb_object_agg(
  g.group_id,
  jsonb_build_object(
    'group_name', g.name,
    'status',     g.status,
    'targets',
      COALESCE((
        SELECT jsonb_agg(
                 jsonb_build_object(
                   'target_id',   t.target_id,
                   'target_type', t.target_type,
                   'identifier',  t.identifier
                 )
                 ORDER BY t.target_id
               )
        FROM target_group_targets gt
        JOIN targets t ON t.target_id = gt.target_id
        WHERE gt.group_id = g.group_id
      ), '[]'::jsonb),
    'rules',
      COALESCE((
        SELECT jsonb_agg(
                 jsonb_build_object(
                   'group_rule_id', gr.group_rule_id,
                   'rule_id',       r.rule_id,
                   'rule_type',     r.rule_type,
                   'name',          r.name,
                   'data_source',   r.data_source,
                   'description',   r.description,
                   'required_fields', r.required_fields,
                   'sql_template',  r.sql_template,
                   'custom_params', gr.custom_params
                 )
                 ORDER BY r.rule_id, gr.group_rule_id
               )
        FROM target_group_rules gr
        JOIN rules r ON r.rule_id = gr.rule_id
        WHERE gr.group_id = g.group_id
      ), '[]'::jsonb)
  )
) AS groups_by_id
FROM target_groups g;
```

If those sanity checks show `0` links, just run the mapping inserts (the 4 targets + 8 rules per group) and re-run the JSON query; it’ll populate immediately.
