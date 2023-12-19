-- SELECT * FROM Organization_attendance a;

-- SELECT 
-- sum(case WHEN role = "LEADER" then 1 else 0 END) as leaderCount,
-- sum(case when role = "CO-LEADER" THEN 1 else 0 END) as coLeaderCount,
-- sum(case when role = "MEMBER" THEN 1 else 0 END) as memberCount,
-- count(*) as total,
-- t.checkInTime,
-- t.checkOutTime
-- FROM Organization_teammember as tm,
-- Organization_team as t

-- WHERE 
-- t.OrganizationId_id = 2 AND
-- TeamId_id = 45 AND
-- t.OrganizationId_id = tm.OrganizationId_id AND
-- t.id = tm.TeamId_id
-- ;

-- SELECT 
-- sum(case when attendance = 1 then 1 else 0 end) as present,
-- sum(case when attendance = 0 then 1 else 0 end) as absent,
-- count(*) as total
-- FROM Organization_attendance a
-- WHERE 
--  TeamId_id = 38 AND
--  Organization_id = 2
-- GROUP BY takenAt;


SELECT * FROM Organization_attendance a
SELECT
id,
sum(case when attendance = 1 then 1 else 0 end) as present,
sum(case when attendance = 0 then 1 else 0 end) as absent,
count(*) as total
FROM Organization_attendance a
WHERE
id <> -1 and
Organization_id = 2 AND
TeamId_id = 48
GROUP BY takenAt;