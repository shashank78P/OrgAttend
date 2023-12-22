-- SELECT * FROM Organization_job_title 
-- where Organization_id = 2;

SELECT * FROM Organization_teammember 
where OrganizationId_id = 2;

SELECT * FROM Organization_employee 
where Organization_id = 2;

SELECT * FROM Organization_job_title 
where Organization_id = 2;

-- SELECT * FROM Organization_employee ;
-- where OrganizationId_id = 2;

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
                    e.employee_id = tm.userId_id AND
                    tm.TeamId_id = 48 AND
                    e.createdAt BETWEEN '2023-11-30' AND '2023-12-30'
                WHERE
                        jt.Organization_id = 2 
                GROUP BY
                    jt.title;