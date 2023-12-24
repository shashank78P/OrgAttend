-- SELECT * from Organization_ownerdetails where userId_id = 3 AND OrganizationId_id = 2;
-- SELECT
--                  TeamId_id
--                 FROM Organization_teammember
--                 WHERE
--                 userId_id = 3
--                 AND
--                 TeamId_id in
--                 (SELECT
--                  TeamId_id
--                 FROM Organization_teammember
--                 WHERE
--                         OrganizationId_id =2 AND

--                     userId_id = 3
--                 );

SELECT
                        *
                    from
                        Organization_ownerdetails
                    where
                        userId_id = 3 AND
                        OrganizationId_id = 2;
-- SELECT userId_id , TeamId_id from Organization_teammember
-- where role in ("LEADER" , "CO-LEADER") AND userId_id = 4;

-- SELECT TeamId_id , role from Organization_teammember
-- where  userId_id = 4;