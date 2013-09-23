-- delete all accounts with empty username:
drop user ''@'localhost' ;
drop user ''@'server' ;
drop user ''@'cloud1' ;
drop user ''@'127.0.0.1' ;

-- delete all 'root' accounts except for 'root'@'localhost'
drop user 'root'@'server' ;
drop user 'root'@'cloud1' ;
drop user 'root'@'127.0.0.1' ;

-- remove all databases whose name starts with 'test':
delete from mysql.db where db like 'test%';
