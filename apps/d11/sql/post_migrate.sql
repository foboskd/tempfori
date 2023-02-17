DROP VIEW IF EXISTS v_d11_doc_field_value CASCADE
;

CREATE OR REPLACE VIEW v_d11_doc_field_value AS
    SELECT
        v.id,
        v.doc_id,
        v.field_id,
        v.value,
        v.created_at,
        v.updated_at,
        f.name AS field_name,
        f.label AS field_label,
        f.type AS field_type

    FROM
        d11_docfieldvalue AS v
        JOIN d11_docfield AS f ON TRUE
            AND v.field_id = f.id
    UNION ALL

    SELECT
        v.id,
        v.doc_id,
        v.field_id,
        TO_JSONB( v.value ) AS value,
        v.created_at,
        v.updated_at,
        f.name AS field_name,
        f.label AS field_label,
        f.type AS field_type

    FROM
        d11_docfilevalue  AS v
        JOIN d11_docfield AS f ON TRUE
            AND v.field_id = f.id
;

-- SELECT * FROM v_d11_doc_field_value;

DROP VIEW IF EXISTS v_d11_doc_values_dates CASCADE
;

CREATE OR REPLACE VIEW v_d11_doc_values_dates AS
    SELECT
        v.doc_id,
        MAX( v.created_at ) AS created_at_max,
        MIN( v.created_at ) AS created_at_min,
        MAX( v.updated_at ) AS updated_at_max,
        MIN( v.updated_at ) AS updated_at_min

    FROM
        d11_docfieldvalue AS v
    GROUP BY
        v.doc_id
;

-- SELECT * FROM v_d11_doc_dates;

DROP MATERIALIZED VIEW IF EXISTS vm_d11_doc_advanced_attributes CASCADE
;

CREATE MATERIALIZED VIEW vm_d11_doc_advanced_attributes AS
    SELECT
        d.id AS doc_id,

        (v_fname.value #>> '{}')::VARCHAR AS full_name,
        (v_ddate.value #>> '{}')::DATE AS defense_date,

        dates.created_at_max AS values_created_at_max,
        dates.created_at_min AS values_created_at_min,
        dates.updated_at_max AS values_updated_at_max,
        dates.updated_at_min AS values_updated_at_min,

        aleph_card_synopsis.id AS aleph_card_synopsis_id,
        aleph_card_synopsis.aleph_id AS aleph_card_synopsis_aleph_id,
        aleph_card_synopsis.created_at AS aleph_card_synopsis_aleph_created_at,
        aleph_card_synopsis.updated_at AS aleph_card_synopsis_aleph_updated_at,

        aleph_card_dissertation.id AS aleph_card_dissertation_id,
        aleph_card_dissertation.aleph_id AS aleph_card_dissertation_aleph_id,
        aleph_card_dissertation.created_at AS aleph_card_dissertation_created_at,
        aleph_card_dissertation.updated_at AS aleph_card_dissertation_updated_at,

        CASE
            WHEN d.last_date_abis_manual_changes IS NOT NULL AND d.last_date_abis_manual_changes < dates.updated_at_max
                THEN TRUE
            ELSE FALSE
        END AS is_has_updates_after_abis_manual_changes

    FROM
        d11_doc                          AS d
        LEFT JOIN v_d11_doc_field_value  AS v_fname ON TRUE
            AND d.id = v_fname.doc_id
            AND v_fname.field_name = 'full_name'
        LEFT JOIN v_d11_doc_field_value  AS v_ddate ON TRUE
            AND d.id = v_ddate.doc_id
            AND v_ddate.field_name = 'defense_date'
        LEFT JOIN v_d11_doc_values_dates AS dates ON TRUE
            AND d.id = dates.doc_id
        LEFT JOIN d11_docalephcard       AS aleph_card_synopsis ON TRUE
            AND d.id = aleph_card_synopsis.doc_id
            AND aleph_card_synopsis.kind = 'synopsis'
        LEFT JOIN d11_docalephcard       AS aleph_card_dissertation ON TRUE
            AND d.id = aleph_card_dissertation.doc_id
            AND aleph_card_dissertation.kind = 'dissertation'
;

CREATE UNIQUE INDEX IF NOT EXISTS vm_d11_doc_advanced_attributes__uniq ON vm_d11_doc_advanced_attributes ( doc_id )
;

-- SELECT * FROM vm_d11_doc_advanced_attributes;

DROP MATERIALIZED VIEW IF EXISTS vm_d11_doc_full_name_doubles CASCADE
;

CREATE MATERIALIZED VIEW vm_d11_doc_full_name_doubles AS
    SELECT
        d.id AS doc_id,
        _.full_name,
        _.docs_ids,
        ARRAY_LENGTH( _.docs_ids, 1 ) AS docs_count
    FROM
        (
            SELECT
                ARRAY_AGG( v.doc_id ) AS docs_ids,
                (v.value #>> '{}')::VARCHAR AS full_name
            FROM
                d11_docfieldvalue AS v
                JOIN d11_docfield AS f ON TRUE
                    AND v.field_id = f.id
                    AND f.name = 'full_name'
            GROUP BY
                full_name
            HAVING
                TRUE
                AND COUNT( v.doc_id ) > 1
        )            AS _
        JOIN d11_doc AS d ON TRUE
            AND d.id = ANY (_.docs_ids)

    WHERE
        TRUE
--     AND _.full_name = 'Народова Екатерина Андреевна'
;

CREATE UNIQUE INDEX IF NOT EXISTS vm_d11_doc_full_name_doubles__uniq ON vm_d11_doc_full_name_doubles ( doc_id )
;

-- SELECT * FROM vm_d11_doc_full_name_doubles;