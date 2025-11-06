-- File: below.sql
-- Parameters:
--   1. object_x_id: The reference object ID, this is the object that we are extruding towards below
--   2. object_y_id: The target object ID , therefore we are checking if y is below object x
--   3. camera_id: The camera ID.
--   4. s: The half-space scale factor.
--   5. tol: The padding tolerance.

WITH params AS (
  SELECT
    CAST(%s AS INTEGER) AS object_x_id,
    CAST(%s AS INTEGER) AS object_y_id,
    CAST(%s AS INTEGER) AS camera_id,
    CAST(%s AS NUMERIC) AS s,     -- half-space scale factor
    CAST(%s AS NUMERIC) AS tol    -- padding tolerance
),
-- 1. Camera
cam AS (
  SELECT position, fov
  FROM camera
  WHERE id = (SELECT camera_id FROM params)
),
-- 2. Object X + centroid
obj_x_info AS (
  SELECT id, name, bbox, ST_Centroid(bbox) AS centroid
  FROM room_objects
  WHERE id = (SELECT object_x_id FROM params)
),
-- 3. Compute rotation so ray→centroid → +Y
rot AS (
  SELECT ST_Azimuth(cam.position, obj_x_info.centroid) AS rot_angle
  FROM cam, obj_x_info
),
-- 4. Transform X into camera space (XY only; Z preserved)
obj_x_trans AS (
  SELECT
    ST_Rotate(
      ST_Translate(o.bbox,
                   -ST_X(cam.position),
                   -ST_Y(cam.position)),
      rot.rot_angle
    ) AS transformed_geom
  FROM room_objects o
  JOIN params ON o.id = params.object_x_id
  CROSS JOIN cam
  CROSS JOIN rot
),
-- 5. Camera‐space 2D envelope for X & Y limits
obj_x_bbox AS (
  SELECT
    env2d,
    ST_XMin(env2d) AS minx,
    ST_XMax(env2d) AS maxx,
    ST_YMin(env2d) AS miny,
    ST_YMax(env2d) AS maxy
  FROM (
    SELECT transformed_geom,
           ST_Envelope(transformed_geom) AS env2d
    FROM obj_x_trans
  ) sub
),
-- 6. True Z‐range of X in world‐space, extended by tol
obj_x_world_z AS (
  SELECT
    ST_ZMin(bbox)        AS bottom_z,
    ST_ZMax(bbox)        AS top_z,
    ST_ZMin(bbox) - tol  AS bottom_z_ext,
    ST_ZMax(bbox) + tol  AS top_z_ext
  FROM obj_x_info
  CROSS JOIN params
),
-- 7. Compute “below” half‐space parameters:
--    • clamp thickness to at least tol,
--    • bottom_z = w_minz,
--    • below_threshold = bottom_z - s·height,
--    • extend X/Y by tol
obj_x_metrics AS (
  SELECT
    wz.bottom_z                                                               AS bottom_z,
    -- clamp object thickness to at least tol
    GREATEST(wz.top_z - wz.bottom_z, params.tol)                               AS height,
    -- threshold downward extrude
    wz.bottom_z - params.s * GREATEST(wz.top_z - wz.bottom_z, params.tol)      AS below_threshold,
    fx.minx                                                                   AS minx,
    fx.maxx                                                                   AS maxx,
    fx.miny                                                                   AS miny,
    fx.maxy                                                                   AS maxy,
    (fx.minx - params.tol)                                                     AS minx_ext,
    (fx.maxx + params.tol)                                                     AS maxx_ext,
    (fx.miny - params.tol)                                                     AS miny_ext,
    (fx.maxy + params.tol)                                                     AS maxy_ext,
    wz.bottom_z_ext                                                            AS w_minz_ext,
    wz.top_z_ext                                                               AS w_maxz_ext
  FROM obj_x_bbox fx
  CROSS JOIN obj_x_world_z wz
  CROSS JOIN params
),
-- 8. Transform Y into camera‐space & dump its 3D points
obj_y_points AS (
  SELECT dp.geom AS pt
  FROM (
    SELECT
      ST_Rotate(
        ST_Translate(o.bbox,
                     -ST_X(cam.position),
                     -ST_Y(cam.position)),
        rot.rot_angle
      ) AS transformed_geom
    FROM room_objects o
    JOIN params ON o.id = params.object_y_id
    CROSS JOIN cam
    CROSS JOIN rot
  ) sub
  CROSS JOIN LATERAL ST_DumpPoints(sub.transformed_geom) AS dp
),
-- 9. Flag “below” if ANY point lies in the padded, clamped prism:
--      Z ∈ [below_threshold, bottom_z]
--  AND X ∈ [minx_ext, maxx_ext]
--  AND Y ∈ [miny_ext, maxy_ext]
flag AS (
  SELECT
    MAX(
      CASE
        WHEN ST_Z(pt) BETWEEN (SELECT below_threshold FROM obj_x_metrics)
                         AND (SELECT bottom_z       FROM obj_x_metrics)
         AND ST_X(pt) BETWEEN (SELECT minx_ext       FROM obj_x_metrics)
                         AND (SELECT maxx_ext       FROM obj_x_metrics)
         AND ST_Y(pt) BETWEEN (SELECT miny_ext       FROM obj_x_metrics)
                         AND (SELECT maxy_ext       FROM obj_x_metrics)
        THEN 1 ELSE 0
      END
    ) AS below_flag
  FROM obj_y_points
)
-- 10. Final output with IDs and human‐readable relation
SELECT
  (SELECT bottom_z         FROM obj_x_metrics) AS obj_x_bottom_z_camera,
  (SELECT height           FROM obj_x_metrics) AS obj_x_height,
  (SELECT below_threshold  FROM obj_x_metrics) AS halfspace_threshold_below_camera,
  flag.below_flag,
  CASE
    WHEN flag.below_flag = 1 THEN
      'Object ' || (SELECT name FROM room_objects WHERE id = (SELECT object_x_id FROM params))
      || ' (ID:' || (SELECT object_x_id FROM params) || ') is below object '
      || (SELECT name FROM room_objects WHERE id = (SELECT object_y_id FROM params))
      || ' (ID:' || (SELECT object_y_id FROM params) || ')'
    ELSE
      'Object ' || (SELECT name FROM room_objects WHERE id = (SELECT object_x_id FROM params))
      || ' (ID:' || (SELECT object_x_id FROM params) || ') is NOT below object '
      || (SELECT name FROM room_objects WHERE id = (SELECT object_y_id FROM params))
      || ' (ID:' || (SELECT object_y_id FROM params) || ')'
  END AS relation
FROM flag;