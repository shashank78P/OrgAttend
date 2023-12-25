-- DELETE
-- FROM
--     Organization_ownerdetails as own
-- WHERE
--     own.OrganizationId_id = 2 AND
--     own.userId_id in (
--         SELECT DISTINCT(u._id) FROM
--             Users_users as u
--         WHERE
--             u.email not in ('19.shashank.p@gmail.com','raki@gmail.com')
--     );

   DELETE
                        FROM
                            Organization_ownerdetails as own
                        WHERE
                            own.OrganizationId_id = 2 AND
                            own.userId_id in (
                                SELECT DISTINCT(u._id) FROM
                                    Users_users as u
                                WHERE
                                    u.email not in ('19.shashank.p@gmail.com', 'raki@gmail.com')
                            );