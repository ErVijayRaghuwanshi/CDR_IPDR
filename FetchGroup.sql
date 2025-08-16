SELECT
  g.group_id as group_id,
  g.name AS group_name,
  t.identifier AS target,
  t.target_id AS target_id,
  t.target_type as target_type,
  r.rule_id AS rule_id,
  r.rule_type AS rule_type,
  r.name AS rule,
  r.data_source AS data_source,
  r.description AS rule_desc,
  r.required_fields AS required_fields,
  r.sql_template as sql_template,
  gr.custom_params
FROM
  target_groups g
  JOIN target_group_targets gt ON g.group_id = gt.group_id
  JOIN targets t ON gt.target_id = t.target_id
  JOIN target_group_rules gr ON g.group_id = gr.group_id
  JOIN rules r ON gr.rule_id = r.rule_id
WHERE
  g.group_id = 'GRP001';





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





