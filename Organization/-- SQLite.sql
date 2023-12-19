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


SELECT * FROM Organization_employee e;

SELECT
        count(e._id) as total,
        jt.title
        FROM Organization_employee as e,
        Organization_job_title as jt,
        Organization_teammember as tm
        where
        e._id <> -1 and
        e.Organization_id = 2 AND
        jt.id = e.jobTitle_id AND
        tm.TeamId_id = 48 AND
        tm.OrganizationId_id = e.Organization_id AND
        e.createdAt BETWEEN '2023-12-03' AND '2023-12-21'
        GROUP BY jt.title;