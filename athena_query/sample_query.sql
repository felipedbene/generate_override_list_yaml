/* Sample Query based on Inventory Data Sync output. 

Details on how to set it up: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-inventory-datasync.html

*/

/* Although AWS-RunPatchBaseline ignores duplicated entries, we are trying to reduce that by using distinct*/
SELECT DISTINCT 'yes' as approved,
	b.value instanceName,
	a.*,
	c.ipv4
FROM (
		(
			(
			/* Get only the patches */
				SELECT *
				FROM "<DATABASE-NAME>"."aws_complianceitem"
				WHERE (compliancetype = 'Patch')
			) a
			/* Get instances names which is technically a tag with key Name */
			LEFT JOIN (
				SELECT *
				FROM "<DATABASE-NAME>"."aws_tag"
				WHERE (key = 'Name')
			) b ON (a.resourceid = b.resourceid)
		)
		/* To get instances ip address */
		INNER JOIN (
			SELECT * 
			FROM "<DATABASE-NAME>"."aws_network"
		) c ON (c.resourceid = b.resourceid)
	)
/* Here we convert the date/time formats so only the current month is displayed as well as only the Missing Patches */
WHERE from_iso8601_timestamp(executiontime) > timestamp '2021-10-01 00:00:00' and patchstate = 'Missing'
