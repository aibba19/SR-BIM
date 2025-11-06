-- File: contains_ratio.sql
-- Params: 1) object1_id, 2) object2_id

WITH p AS (
  SELECT
    %s::integer AS id1,
    %s::integer AS id2
),
xgeom AS (
  SELECT bbox AS geom_x
  FROM room_objects
  WHERE id = (SELECT id1 FROM p)
),
ygeom AS (
  SELECT bbox AS geom_y
  FROM room_objects
  WHERE id = (SELECT id2 FROM p)
),
dims_x AS (
  SELECT
    ST_XMin(geom_x) AS xmin_x, ST_XMax(geom_x) AS xmax_x,
    ST_YMin(geom_x) AS ymin_x, ST_YMax(geom_x) AS ymax_x,
    ST_ZMin(geom_x) AS zmin_x, ST_ZMax(geom_x) AS zmax_x
  FROM xgeom
),
dims_y AS (
  SELECT
    ST_XMin(geom_y) AS xmin_y, ST_XMax(geom_y) AS xmax_y,
    ST_YMin(geom_y) AS ymin_y, ST_YMax(geom_y) AS ymax_y,
    ST_ZMin(geom_y) AS zmin_y, ST_ZMax(geom_y) AS zmax_y
  FROM ygeom
),
overlap AS (
  SELECT
    GREATEST(0, LEAST(xmax_x, xmax_y) - GREATEST(xmin_x, xmin_y)) AS ov_x,
    GREATEST(0, LEAST(ymax_x, ymax_y) - GREATEST(ymin_x, ymin_y)) AS ov_y,
    GREATEST(0, LEAST(zmax_x, zmax_y) - GREATEST(zmin_x, zmin_y)) AS ov_z
  FROM dims_x
  CROSS JOIN dims_y
),
vols AS (
  SELECT
    ov_x, ov_y, ov_z,
    (xmax_x - xmin_x) * (ymax_x - ymin_x) * (zmax_x - zmin_x) AS vol_x,
    ov_x * ov_y * ov_z                                AS vol_i
  FROM overlap
  CROSS JOIN dims_x
)
SELECT
  (vol_i > 0)::int AS is_contained,
  CASE
    WHEN vol_x = 0 THEN NULL
    ELSE vol_i / vol_x
  END AS pct_contained,
  CASE
    WHEN vol_i > 0 THEN
      o1.name || ' (ID:' || o1.id || ') is contained '
      || ROUND((vol_i / vol_x)::numeric, 3)
      || ' in ' || o2.name || ' (ID:' || o2.id || ')'
    ELSE
      o1.name || ' (ID:' || o1.id || ') is NOT contained in '
      || o2.name || ' (ID:' || o2.id || ')'
  END AS relation
FROM vols
JOIN room_objects o1 ON o1.id = (SELECT id1 FROM p)
JOIN room_objects o2 ON o2.id = (SELECT id2 FROM p);
