SELECT a.*, COUNT(a.id) AS total_days,
SUM(CASE WHEN a.attendance = 1 THEN 1 ELSE 0 END) AS days_present,
SUM(CASE WHEN a.attendance = 0 THEN 1 ELSE 0 END) AS days_absent
FROM Organization_attendance a 
 WHERE a.TeamId_id = 45 GROUP BY a.userId_id ORDER BY a.userId_id;
-- SELECT
--     u._id AS user_id

--     u.firstName AS user_first_name

--     COUNT(a.id) AS total_days,
--     SUM(CASE WHEN a.attendance = 1 THEN 1 ELSE 0 END) AS days_present,
--     SUM(CASE WHEN a.attendance = 0 THEN 1 ELSE 0 END) AS days_absent,
--     MIN(a.createdAt) AS first_attendance_date,
--     MAX(a.updatedAt) AS last_attendance_date
-- FROM
--     Users_users u
-- LEFT JOIN
--     Organization_attendance a ON u._id = a.userId_id
-- WHERE
--     a.TeamId_id = 45
-- GROUP BY
--     u._id, u.firstName
-- ORDER BY
--     u.firstName;
