select
                jt.title as title,
                id
            from Organization_job_title as jt
            where
            id in
            (select
                DISTINCT(e.jobTitle_id)
            FROM
                Organization_team as t,
                Organization_teammember as tm,
                Organization_employee as e
            WHERE
                t.id IN (1, 38, 45, 48) AND
                e.employee_id = 3 AND
                e.Organization_id = 2 AND
                e.Organization_id = t.OrganizationId_id AND
                tm.OrganizationId_id = t.OrganizationId_id AND
                e.employee_id = tm.userId_id
            );