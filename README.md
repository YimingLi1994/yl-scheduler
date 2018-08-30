V 0.2.0 EVENT DRIVEN

To use this scheduler you need to have:
python MySQL package

the dependent folder is to store the dependent file
that can be triggerred in deptable
it can only accept return code 0
other wise it will trigger error
return value of 0 or 1
0 is passed
1 is not passed
do this until dependent time out

the jobfolder is to store the job
that can be triggerred in jobtable
when return code is not 0 it will send message to schedulerDB.schedulerMessage


# Code to create table

##For main
```sql
BEGIN;
create table schedulerDB.deptable
(
	id bigint(20) unsigned not null auto_increment
		primary key,
	jobchainid bigint(20) unsigned not null,
	env varchar(1024) default '/usr/bin/python3' null,
	command varchar(200) not null,
	entry_time timestamp default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
	`desc` varchar(50) null,
	ottime int not null,
	constraint id_UNIQUE
		unique (id)
);
create table schedulerDB.jobchain_table
(
	id bigint(20) unsigned not null auto_increment
		primary key,
	job_desc varchar(50) null,
	total_stpes int(6) unsigned not null,
	entry_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	timestr varchar(30) not null,
	dep_ot float not null,
	switch varchar(5) default 'ON' not null,
	main_flag int default '1' not null,
	BKP_flag int default '0' not null,
	tag varchar(45) null,
	subtag varchar(45) null
);


--
-- Create model Jobtable
--
create table schedulerDB.jobtable
(
	id bigint(20) unsigned not null auto_increment
		primary key,
	env varchar(1024) default '/usr/bin/python3' null,
	job_chain_id bigint(20) unsigned not null,
	job_desc varchar(45) null,
	command varchar(200) not null,
	step_lvl int(6) not null,
	ottime varchar(30) not null,
	entry_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

--
-- Add field jobchainid to deptable
--

USE schedulerDB;
ALTER TABLE `jobtable`
ADD FOREIGN KEY (`job_chain_id`)
REFERENCES `jobchain_table` (`id`)
ON DELETE CASCADE;
ALTER TABLE `deptable`
ADD FOREIGN KEY (`jobchainid`)
REFERENCES `jobchain_table` (`id`)
ON DELETE CASCADE;
COMMIT;

BEGIN;
create table schedulerDB.jobchain_lst_run
(
	id bigint(20) unsigned not null auto_increment
		primary key,
	jobchain_id bigint(20) unsigned not null not null,
	last_run_start timestamp null,
	last_run_end timestamp null,
	pid int null,
	status varchar(20) default 'RUNNING...' null,
	dep_pass_ts timestamp null
);


--
-- Create model RealtimeStatus_MAIN
--
CREATE TABLE schedulerDB.realtime_status (
  `id` bigint(20) unsigned not null AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `timequeuesize` int(11) DEFAULT '0',
  `replyqueuesize` int(11) DEFAULT '0',
  `debugmode` varchar(45) NOT NULL DEFAULT 'debug',
  `index_last_ping_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `pid_index` int(11) DEFAULT NULL,
  `pid_timer` int(11) DEFAULT NULL,
  `pid_sqlfetcher` int(11) DEFAULT NULL,
  `pid_receiver` int(11) DEFAULT NULL,
  `job_last_ping_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);
--
-- Create model Schedulermessage_MAIN
--

CREATE TABLE schedulerDB.schedulerMessage (
  `id` bigint(20) unsigned not null AUTO_INCREMENT,
  `run_id` bigint(20) DEFAULT NULL,
  `msg` varchar(5000) DEFAULT NULL,
  `entry_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);
commit;

```
# How to run
The entrance is index.py no parameter needed. 

When start a new scheduler, the main and bkp mysql
connectioninfo is needed

