SELECT
                t.id,
                t.name as teamName,
                t.checkInTime as checkInTime,
                t.checkOutTime as checkOutTime,
                takenAt AS takenAt,
                a.attendance as attendance
            FROM
                Organization_team as t
            LEFT JOIN
                Organization_attendance as a ON t.id = a.TeamId_id
            WHERE
                t.id IN (1, 38, 45, 48) AND
                a.Organization_id = 2 AND
                a.takenAt ='2023-12-19';