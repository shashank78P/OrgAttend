SELECT
            takenAt AS takenAt,
            SUM(CASE WHEN attendance = 1 THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN attendance = 0 THEN 1 ELSE 0 END) AS absent,
            COUNT(takenAt) AS total,
            id
        FROM
            Organization_attendance AS a
        where
            id <> -1 and
            TeamId_id = 54 and
            takenAt between '2023-01-01' and '2023-12-31'
        GROUP BY
            takenAt ORDER BY takenAt;