-- File: contains.sql
-- Params: 1) object1_id,  2) object2_id

WITH p AS (
  SELECT
    %s::integer AS id1,
    %s::integer AS id2
)
SELECT
  CASE
    WHEN ST_Covers(o2.bbox, o1.bbox)
      THEN 
        o1.name || ' (ID:' || o1.id || ') is contained in ' ||
        o2.name || ' (ID:' || o2.id || ')'
    ELSE 
        o1.name || ' (ID:' || o1.id || ') is NOT contained in ' ||
        o2.name || ' (ID:' || o2.id || ')'
  END AS relation,
  (ST_Covers(o2.bbox, o1.bbox))::int       AS is_contained,
  (NOT ST_Covers(o2.bbox, o1.bbox))::int   AS is_not_contained
FROM p
JOIN room_objects AS o1
  ON o1.id = p.id1
JOIN room_objects AS o2
  ON o2.id = p.id2;
