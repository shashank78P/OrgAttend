SELECT
    tm.*,
    a.*,
    COUNT(a.id) AS total_days,
    SUM(CASE WHEN a.attendance = 1 THEN 1 ELSE 0 END) AS days_present,
    SUM(CASE WHEN a.attendance = 0 THEN 1 ELSE 0 END) AS days_absent
FROM
    Organization_teammember tm
LEFT JOIN
    Users_users AS u ON tm.userId_id = u._id
LEFT JOIN
    Organization_attendance AS a ON a.userId_id = u._id AND a.TeamId_id = tm.TeamId_id
WHERE
    tm.TeamId_id = 48
GROUP BY
    tm.userId_id
ORDER BY
    u.firstName, u.middleName, u.lastName;
