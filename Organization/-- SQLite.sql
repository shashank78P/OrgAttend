-- SELECT * FROM Organization_job_title 
-- where Organization_id = 2;

-- SELECT * FROM Organization_teammember 
-- where OrganizationId_id = 2 AND
-- TeamId_id in (1, 38, 45, 48)
-- ;

SELECT
    jt.title as jobTitle,
    count(e.employee_id) as total,
    jt.id
FROM
    Organization_job_title as jt,
    Organization_teammember as tm
LEFT JOIN
    Organization_employee as e ON
    e.jobTitle_id = jt.id AND
    e.Organization_id = 2 AND
    jt.Organization_id = e.Organization_id AND
    e.employee_id = tm.userId_id AND
    tm.TeamId_id = 48 AND
    e.createdAt BETWEEN '2023-12-01' AND '2023-12-31'
WHERE
        jt.Organization_id = 2
GROUP BY
                    jt.title;