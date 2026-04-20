import re
from collections import OrderedDict
from typing import Dict, List, Set, Tuple, Optional, Pattern


SQL_KEYWORDS_BASE = {
    "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL",
    "ON", "AS", "AND", "OR", "NOT", "IN", "LIKE", "EXISTS", "BETWEEN", "IS", "NULL",
    "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL", "DISTINCT",
    "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "DROP",
    "ALTER", "ADD", "COLUMN", "CONSTRAINT", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
    "UNIQUE", "INDEX", "VIEW", "TRIGGER", "PROCEDURE", "FUNCTION", "RETURN", "CALL",
    "COMMIT", "ROLLBACK", "SAVEPOINT", "TRANSACTION", "BEGIN", "END", "IF", "ELSE",
    "CASE", "WHEN", "THEN", "ELSEIF", "WHILE", "LOOP", "FOR", "CURSOR", "OPEN",
    "CLOSE", "FETCH", "DECLARE", "TRUE", "FALSE", "ASC", "DESC", "TOP", "PERCENT",
    "WITH", "TIES", "ONLY", "FIRST", "NEXT", "ROW", "ROWS", "OVER", "PARTITION",
    "RANK", "DENSE_RANK", "ROW_NUMBER", "NTILE", "LEAD", "LAG", "FIRST_VALUE",
    "LAST_VALUE", "NTH_VALUE", "CUME_DIST", "PERCENT_RANK", "PERCENTILE_CONT",
    "PERCENTILE_DISC", "WITHIN", "ARRAY", "MULTISET", "XML", "JSON", "TABLESAMPLE",
    "SYSTEM", "BERNOULLI", "REPEATABLE", "COMMITTED", "UNCOMMITTED", "SERIALIZABLE",
    "READ", "WRITE", "ONLY", "ISOLATION", "LEVEL", "ACCESS", "MODE", "DIAGNOSTICS",
    "CONDITION", "CURRENT", "DATE", "TIME", "TIMESTAMP", "DATETIME", "INTERVAL",
    "YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND", "MICROSECOND", "NOW",
    "CURDATE", "CURTIME", "LOCALTIME", "LOCALTIMESTAMP", "UTC_DATE", "UTC_TIME",
    "UTC_TIMESTAMP", "UNIX_TIMESTAMP", "FROM_UNIXTIME", "STR_TO_DATE", "DATE_FORMAT",
    "TIME_FORMAT", "YEARWEEK", "WEEKOFYEAR", "DAYOFYEAR", "DAYOFMONTH", "DAYOFWEEK",
    "WEEKDAY", "QUARTER", "PERIOD_ADD", "PERIOD_DIFF", "TO_DAYS", "FROM_DAYS",
    "MAKEDATE", "MAKETIME", "SEC_TO_TIME", "TIME_TO_SEC", "ADDDATE", "SUBDATE",
    "ADDTIME", "SUBTIME", "DATE_ADD", "DATE_SUB", "DATEDIFF", "TIMESTAMPADD",
    "TIMESTAMPDIFF", "CONVERT_TZ", "FORMAT", "INET_ATON", "INET_NTOA", "INET6_ATON",
    "INET6_NTOA", "UUID", "UUID_SHORT", "MD5", "SHA1", "SHA2", "RAND", "ROUND",
    "FLOOR", "CEIL", "CEILING", "ABS", "SIGN", "MOD", "DIV", "POW", "POWER", "SQRT",
    "EXP", "LN", "LOG", "LOG2", "LOG10", "PI", "TRUNCATE", "RADIANS", "DEGREES",
    "SIN", "COS", "TAN", "COT", "ASIN", "ACOS", "ATAN", "ATAN2", "CONV", "BIN",
    "OCT", "HEX", "UNHEX", "CHAR_LENGTH", "CHARACTER_LENGTH", "LENGTH", "BIT_LENGTH",
    "CONCAT", "CONCAT_WS", "INSTR", "LOCATE", "POSITION", "LPAD", "RPAD", "LEFT",
    "RIGHT", "SUBSTRING", "SUBSTR", "MID", "SUBSTRING_INDEX", "TRIM", "LTRIM", "RTRIM",
    "REPLACE", "REPEAT", "REVERSE", "ELT", "FIELD", "FIND_IN_SET", "MAKE_SET", "SPACE",
    "STRCMP", "SOUNDEX", "REGEXP", "RLIKE", "BINARY", "CAST", "CONVERT", "COALESCE",
    "IFNULL", "NULLIF", "GREATEST", "LEAST", "INTERVAL", "DEFAULT", "VALUES",
    "LAST_INSERT_ID", "ROW_COUNT", "FOUND_ROWS", "CONNECTION_ID", "CURRENT_USER",
    "SESSION_USER", "SYSTEM_USER", "USER", "DATABASE", "SCHEMA", "VERSION", "CHARSET",
    "COLLATION", "COERCIBILITY", "CHAR", "ASCII", "ORD", "QUOTE", "BIT_COUNT",
    "GET_LOCK", "RELEASE_LOCK", "IS_FREE_LOCK", "IS_USED_LOCK", "RELEASE_ALL_LOCKS",
    "NAME_CONST", "SLEEP", "BENCHMARK", "LAST_DAY", "TIMEDIFF", "SEPARATOR", "MATCH",
    "AGAINST", "BOOLEAN", "MODE", "NATURAL", "LANGUAGE", "QUERY", "EXPANSION",
    "AUTO_INCREMENT", "SQL_CALC_FOUND_ROWS", "SQL_BIG_RESULT", "SQL_SMALL_RESULT",
    "SQL_BUFFER_RESULT", "SQL_CACHE", "SQL_NO_CACHE", "FOR", "UPDATE", "LOCK", "SHARE",
    "PROCEDURE", "ANALYSE", "STARTS", "ENDS", "OPTION", "OPTIONALLY", "ENCLOSED",
    "ESCAPED", "TERMINATED", "LINES", "STARTING", "CLOSED", "LOCAL", "GLOBAL",
    "TEMPORARY", "TEMP", "DELAYED", "HIGH_PRIORITY", "LOW_PRIORITY", "QUICK",
    "DELAY_KEY_WRITE", "IGNORE", "FORCE", "STRAIGHT_JOIN", "USE", "DISTINCTROW", "DUAL",
    "DUPLICATE", "CHECK", "COMMENT", "ENGINE", "CHARACTER", "SET", "COLLATE",
    "ROW_FORMAT", "COMPRESSION", "BLOCK_SIZE", "PERSISTENT", "PAGE_CHECKSUM", "CHECKSUM",
    "INSERT_METHOD", "MAX_ROWS", "MIN_ROWS", "AVG_ROW_LENGTH", "PACK_KEYS",
    "STATS_AUTO_RECALC", "STATS_PERSISTENT", "STATS_SAMPLE_PAGES", "DATA_DIRECTORY",
    "INDEX_DIRECTORY", "TABLESPACE", "STORAGE", "UNION", "RAID_TYPE", "RAID_CHUNKS",
    "RAID_CHUNKSIZE", "INITIAL", "NEXT", "MINVALUE", "MAXVALUE", "START", "INCREMENT",
    "CACHE", "CYCLE", "NOCYCLE", "NOMINVALUE", "NOMAXVALUE", "NOORDER", "ORDER",
    "BEFORE", "AFTER", "INSTEAD", "OF", "EACH", "STATEMENT", "OLD", "NEW", "FOLLOWS",
    "PRECEDES", "SQLSTATE", "SQLWARNING", "NOTFOUND", "SQLEXCEPTION", "CONTINUE",
    "EXIT", "UNDO", "SIGNAL", "RESIGNAL", "LEAVE", "ITERATE", "REPEAT", "UNTIL",
    "RETURNS", "DETERMINISTIC", "CONTAINS", "NOSQL", "NO", "READS", "DATA", "MODIFIES",
    "SECURITY", "DEFINER", "INVOKER", "AUTHID", "ATOMIC", "PARAMETER", "STYLE",
    "GENERAL", "INHERIT", "EVENT", "SCHEDULE", "EVERY", "AT", "ENABLE", "DISABLE",
    "COMPLETION", "PRESERVE", "DO", "SHOW", "BINLOG", "EVENTS", "LOGS", "SLAVE",
    "HOSTS", "MASTER", "STATUS", "ENGINES", "PROCESSLIST", "FULL", "OPEN", "TABLES",
    "DATABASES", "SCHEMAS", "COLUMNS", "FIELDS", "KEYS", "PRIVILEGES", "GRANTS",
    "SERVER", "LOGFILE", "RENAME", "TO", "USING", "ROLLUP", "CUBE", "PIVOT", "UNPIVOT",
    "ROWS", "FETCH", "NOWAIT", "SKIP", "LOCKED", "PARTITION", "PARTITIONS", "SUBPARTITION",
    "SUBPARTITIONS", "LESS", "THAN", "MAXVALUE", "IN", "VISIBLE", "INVISIBLE", "GENERATED",
    "ALWAYS", "VIRTUAL", "STORED", "SIGNED", "UNSIGNED", "ZEROFILL", "BIT", "TINYINT",
    "SMALLINT", "MEDIUMINT", "INT", "INTEGER", "BIGINT", "FLOAT", "DOUBLE", "PRECISION",
    "REAL", "DECIMAL", "DEC", "NUMERIC", "BOOLEAN", "BOOL", "SERIAL", "CHAR", "VARCHAR",
    "TINYTEXT", "TEXT", "MEDIUMTEXT", "LONGTEXT", "BINARY", "VARBINARY", "TINYBLOB",
    "BLOB", "MEDIUMBLOB", "LONGBLOB", "ENUM", "GEOMETRY", "POINT", "LINESTRING",
    "POLYGON", "MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON", "GEOMETRYCOLLECTION",
    "JSONB", "VARYING", "NATIONAL", "NCHAR", "NVARCHAR", "FIXED", "DYNAMIC",
    "COMPRESSED", "REDUNDANT", "COMPACT", "PLAN", "EXPLAIN", "ANALYZE", "OPTIMIZE",
    "REPAIR", "CHECK", "BACKUP", "RESTORE", "IMPORT", "EXPORT", "FLUSH", "RESET",
    "KILL", "PURGE", "REVOKE", "GRANT", "IDENTIFIED", "PASSWORD", "REQUIRE", "SSL",
    "X509", "CIPHER", "ISSUER", "SUBJECT", "VALID", "UNTIL", "WITH", "GRANT", "OPTION",
    "MAX_QUERIES_PER_HOUR", "MAX_UPDATES_PER_HOUR", "MAX_CONNECTIONS_PER_HOUR",
    "MAX_USER_CONNECTIONS", "ROLE", "SET", "DEFAULT", "ROLE", "SUPER", "EXECUTE",
    "PROCESS", "FILE", "SHUTDOWN", "RELOAD", "SHOW", "DATABASES", "REPLICATION",
    "SLAVE", "CLIENT", "CREATE", "USER", "EVENT", "FUNCTION", "PROCEDURE", "TRIGGER",
    "VIEW", "ROUTINE", "CREATE", "DROP", "ALTER", "REFERENCES", "INDEX", "CREATE",
    "DROP", "EVENT", "CREATE", "DROP", "ALTER", "EXECUTE", "TRIGGER", "CREATE",
    "DROP", "ALTER", "VIEW", "CREATE", "DROP", "GRANT", "REVOKE", "LOCK", "TABLES",
    "UNLOCK", "TABLES", "START", "TRANSACTION", "COMMIT", "ROLLBACK", "SAVEPOINT",
    "RELEASE", "SAVEPOINT", "SET", "ISOLATION", "LEVEL", "AUTOCOMMIT", "STARTING",
    "COMMITTED", "REPEATABLE", "SERIALIZABLE", "READ", "WRITE", "ONLY", "ACCESS",
    "MODE", "IN", "SHARE", "EXCLUSIVE", "MODE", "PREPARE", "EXECUTE", "DEALLOCATE",
    "PREPARE", "USING", "DELIMITER", "HANDLER", "OPEN", "CLOSE", "READ", "FIRST",
    "NEXT", "PREV", "LAST", "IDENTIFIED", "BY", "WITH", "MALLOC_ERROR", "DUMP",
    "DUMPFILE", "OUTFILE", "INFILE", "LOAD", "DATA", "LOW_PRIORITY", "LOCAL", "INFILE",
    "REPLACE", "IGNORE", "FIELDS", "COLUMNS", "LINES", "TERMINATED", "OPTIONALLY",
    "ENCLOSED", "ESCAPED", "STARTING", "IGNORE", "LINES", "CHARACTER", "SET", "INTO",
    "TABLE", "PARTITION", "PARTITIONS", "SET", "CHARACTER", "SET", "NAMES", "COLLATION",
    "TRANSACTION", "SIGNAL", "RESIGNAL", "CONDITION", "OUT", "INOUT", "VARIADIC",
    "DETERMINISTIC", "MODIFIES", "SQL", "DATA", "CONTAINS", "SQL", "NO", "SQL",
    "READS", "SQL", "DATA", "EXTERNAL", "LANGUAGE", "SQL", "PARAMETER", "STYLE",
    "SQL", "CONTAINS", "SQL", "NO", "SQL", "READS", "SQL", "DATA", "MODIFIES", "SQL",
    "DATA", "CALLED", "ON", "NULL", "INPUT", "RETURNS", "NULL", "ON", "NULL",
    "INPUT", "STATIC", "DYNAMIC", "RESULT", "SET", "WITH", "RETURN", "CARDINALITY",
    "AS", "LOCATOR", "CLOB", "BLOB", "NCLOB", "XML", "JSON", "ROW", "TYPE",
    "TABLE", "OF", "REF", "CONSTRAINT", "TRIGGER", "SCHEMA", "DOMAIN", "SEQUENCE",
    "TRANSLATION", "ASSERTION", "CHARACTER", "SET", "COLLATION", "TYPE", "DOMAIN",
    "ROW", "TYPE", "MULTISET", "TYPE", "ARRAY", "TYPE", "DISTINCT", "TYPE", "USER",
    "DEFINED", "TYPE", "UNDER", "SUBTYPE", "TREAT", "VALUE", "OF", "REF", "IS",
    "NOT", "NULL", "MEMBER", "OF", "SUBMULTISET", "MOD", "SIMILAR", "TO", "OVERLAPS",
    "PARTITION", "RANGE", "LIST", "HASH", "COMPOSITE", "HASHKEYS", "SUFFIX", "PREFIX",
    "SUBPARTITION", "BY", "RANGE", "HASH", "LINEAR", "HASH", "KEY", "LINEAR", "KEY",
    "ALGORITHM", "DEFAULT", "INPLACE", "COPY", "NOCOPY", "FORCE", "SWAP", "WITH",
    "VALIDATION", "WITHOUT", "VALIDATION", "ONLINE", "OFFLINE", "LOCK", "NONE", "SHARE",
    "EXCLUSIVE", "NOWAIT", "WAIT", "USING", "BTREE", "HASH", "RTREE", "FULLTEXT",
    "SPATIAL", "VISIBLE", "INVISIBLE", "KEY_BLOCK_SIZE", "USING", "COMMENT", "DATA",
    "INDEX", "DIRECTORY", "ENGINE", "ENGINE_ATTRIBUTE", "SECONDARY_ENGINE",
    "SECONDARY_ENGINE_ATTRIBUTE", "ENGINE_ATTRIBUTE", "SECONDARY_ENGINE_ATTRIBUTE",
    "INSERT_METHOD", "NO", "DELAY_KEY_WRITE", "DELAY_KEY_WRITE", "ROW_FORMAT",
    "DEFAULT", "DYNAMIC", "FIXED", "COMPRESSED", "REDUNDANT", "COMPACT", "STATS_PERSISTENT",
    "STATS_AUTO_RECALC", "STATS_SAMPLE_PAGES", "CHECKSUM", "DELAY_KEY_WRITE",
    "PACK_KEYS", "MIN_ROWS", "MAX_ROWS", "AVG_ROW_LENGTH", "PASSWORD", "UNCOMPRESS",
    "COMPRESS", "AUTO_INCREMENT", "AVG_ROW_LENGTH", "CHECKSUM", "COMPRESSION",
    "CONNECTION", "DATA", "DIRECTORY", "DELAY_KEY_WRITE", "ENGINE", "INSERT_METHOD",
    "KEY_BLOCK_SIZE", "MAX_ROWS", "MIN_ROWS", "PACK_KEYS", "ROW_FORMAT", "STATS_AUTO_RECALC",
    "STATS_PERSISTENT", "STATS_SAMPLE_PAGES", "TABLESPACE", "UNION", "ENGINE_ATTRIBUTE",
    "SECONDARY_ENGINE_ATTRIBUTE", "CONSTRAINT", "NOT", "DEFERRABLE", "INITIALLY",
    "DEFERRED", "IMMEDIATE", "DEFERRABLE", "INITIALLY", "DEFERRED", "IMMEDIATE",
    "INITIALLY", "DEFERRED", "IMMEDIATE", "DEFERRABLE", "INITIALLY", "DEFERRED",
    "IMMEDIATE", "INITIALLY", "DEFERRED", "IMMEDIATE", "INITIALLY", "DEFERRED",
    "IMMEDIATE", "INITIALLY", "DEFERRED", "IMMEDIATE", "INITIALLY", "DEFERRED",
    "IMMEDIATE", "INITIALLY", "DEFERRED", "IMMEDIATE", "INITIALLY", "DEFERRED",
}

DAMA_SPECIFIC_KEYWORDS = {
    "ROWNUM", "ROWID", "LEVEL", "CONNECT", "PRIOR", "START", "NOCYCLE",
    "SYSDATE", "SYSTIMESTAMP", "DBTIMEZONE", "SESSIONTIMEZONE",
    "TO_CHAR", "TO_DATE", "TO_NUMBER", "TO_TIMESTAMP",
    "NVL", "NVL2", "DECODE", "WM_CONCAT",
    "SYS_CONNECT_BY_PATH", "CONNECT_BY_ISLEAF", "CONNECT_BY_ISCYCLE",
    "CONNECT_BY_ROOT", "NEXTVAL", "CURRVAL", "SEQUENCE",
    "CREATE", "OR", "REPLACE", "PACKAGE", "BODY",
    "LANGUAGE", "C", "JAVA", "EXTERNAL", "NAME",
    "PARALLEL_ENABLE", "PIPELINED", "RESULT_CACHE",
    "CLUSTER", "ORGANIZATION", "HEAP", "EXTERNAL",
    "MATERIALIZED", "VIEW", "REFRESH", "FAST", "COMPLETE", "FORCE",
    "ON", "COMMIT", "DEMAND", "START", "NEXT", "USING",
    "ROLLBACK", "SEGMENT", "ENABLE", "DISABLE", "NOVALIDATE", "VALIDATE",
    "EXCEPTION", "INTO", "CASCADE", "USING", "INDEX",
    "PCTFREE", "PCTUSED", "INITRANS", "MAXTRANS", "STORAGE",
    "INITIAL", "NEXT", "MINEXTENTS", "MAXEXTENTS", "PCTINCREASE",
    "OPTIMAL", "BUFFER_POOL", "KEEP", "RECYCLE", "DEFAULT",
    "ORDER", "NOORDER", "CYCLE", "NOCYCLE", "MINVALUE", "MAXVALUE",
    "INCREMENT", "BY", "RANGE", "LIST", "HASH", "SUBPARTITION",
    "SUBPARTITIONS", "SYNONYM", "PUBLIC", "LINK", "DATABASE",
    "LOGGING", "NOLOGGING", "COMPRESS", "NOCOMPRESS", "CACHE", "NOCACHE",
    "TEMPORARY", "PERMANENT", "TABLESPACE", "DATAFILE",
    "SCHEMA", "ROLE", "PUBLIC", "GRANT", "REVOKE", "IDENTIFIED",
    "PRIVILEGES", "WITH", "ADMIN", "OPTION",
    "ANALYZE", "COMPUTE", "STATISTICS", "ESTIMATE", "SAMPLE",
    "BLOCK", "ROWS", "STRUCTURE", "CHAINED", "LIST",
    "EXPLAIN", "PLAN", "SET", "STATEMENT", "ID", "SNAPSHOT",
    "TOO", "OLD", "CONSTRAINTS", "DEFERRED", "IMMEDIATE",
    "ISOLATION", "LEVEL", "SERIALIZABLE", "REPEATABLE", "COMMITTED",
    "UNCOMMITTED", "AUTOCOMMIT", "LOCK", "IN", "EXCLUSIVE",
    "SHARE", "UPDATE", "MODE", "NOWAIT", "WORK", "FORCE",
    "RELEASE", "SAVEPOINT", "DECLARE", "EXIT", "WHEN", "EXCEPTION",
    "RAISE", "RAISE_APPLICATION_ERROR", "PRAGMA", "AUTONOMOUS_TRANSACTION",
    "EXCEPTION_INIT", "SERIALLY_REUSABLE", "RESTRICT_REFERENCES",
    "WRAPPER", "SPECIFICATION", "AUTHID", "CURRENT_USER", "ATOMIC",
    "NOT", "NULL", "PARAMETER", "STYLE", "GENERAL", "SQL", "INHERIT",
    "EVENT", "SCHEDULE", "EVERY", "AT", "COMPLETION", "PRESERVE",
    "BINLOG", "HOSTS", "MASTER", "STATUS", "ENGINES", "PROCESSLIST",
    "OPEN", "TABLES", "DATABASES", "SCHEMAS", "COLUMNS", "FIELDS",
    "INDEX", "KEYS", "USER", "EVENT", "FUNCTION", "PROCEDURE",
    "SERVER", "LOGFILE", "TABLESPACE", "VIEW", "INDEX", "CONSTRAINT",
    "REFERENCE", "RENAME", "TO", "LIKE", "RLIKE", "MATCH", "AGAINST",
    "USING", "ROLLUP", "CUBE", "PIVOT", "UNPIVOT", "ROWS", "FETCH",
    "ONLY", "TIES", "WITH", "FOR", "UPDATE", "SHARE", "MODE",
    "NOWAIT", "SKIP", "LOCKED", "OF", "TABLE", "PARTITION",
    "PARTITIONS", "SUBPARTITION", "SUBPARTITIONS", "VALUES", "LESS",
    "THAN", "MAXVALUE", "IN", "EACH", "ROW", "STORAGE", "ENGINE",
    "COMMENT", "DATA", "INDEX", "DIRECTORY", "MIN_ROWS", "MAX_ROWS",
    "AVG_ROW_LENGTH", "PACK_KEYS", "CHECKSUM", "DELAY_KEY_WRITE",
    "ROW_FORMAT", "COMPRESSION", "BLOCK_SIZE", "PAGE_CHECKSUM",
    "PERSISTENT", "STATS_AUTO_RECALC", "STATS_PERSISTENT", "STATS_SAMPLE_PAGES",
    "TABLESPACE", "STORAGE", "UNION", "INSERT_METHOD", "AUTO_INCREMENT",
    "DEFAULT", "CHARACTER", "SET", "COLLATE", "UNIQUE", "PRIMARY",
    "KEY", "INDEX", "CONSTRAINT", "FOREIGN", "REFERENCES", "REFERENCE",
    "ON", "DELETE", "UPDATE", "CASCADE", "SET", "NULL", "NO", "ACTION",
    "RESTRICT", "CHECK", "COMMENT", "AS", "VISIBLE", "INVISIBLE",
    "GENERATED", "ALWAYS", "VIRTUAL", "STORED", "SIGNED", "UNSIGNED",
    "ZEROFILL", "AUTO_INCREMENT", "UNIQUE", "PRIMARY", "KEY", "INDEX",
    "CONSTRAINT", "FOREIGN", "REFERENCES", "REFERENCE", "ON", "DELETE",
    "UPDATE", "CASCADE", "SET", "NULL", "NO", "ACTION", "RESTRICT",
    "CHECK", "COMMENT", "AS", "VISIBLE", "INVISIBLE", "GENERATED",
    "ALWAYS", "VIRTUAL", "STORED", "SIGNED", "UNSIGNED", "ZEROFILL",
    "BIT", "TINYINT", "SMALLINT", "MEDIUMINT", "INT", "INTEGER", "BIGINT",
    "FLOAT", "DOUBLE", "PRECISION", "REAL", "DECIMAL", "DEC", "NUMERIC",
    "BOOLEAN", "BOOL", "SERIAL", "DATE", "DATETIME", "TIMESTAMP", "TIME",
    "YEAR", "CHAR", "VARCHAR", "TINYTEXT", "TEXT", "MEDIUMTEXT", "LONGTEXT",
    "BINARY", "VARBINARY", "TINYBLOB", "BLOB", "MEDIUMBLOB", "LONGBLOB",
    "ENUM", "SET", "GEOMETRY", "POINT", "LINESTRING", "POLYGON",
    "MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON", "GEOMETRYCOLLECTION",
    "JSON", "JSONB", "VARYING", "CHARACTER", "NATIONAL", "NCHAR", "NVARCHAR",
    "FIXED", "DYNAMIC", "COMPRESSED", "REDUNDANT", "COMPACT", "ROW_FORMAT",
    "COMPRESSION", "BLOCK_SIZE", "PAGE_CHECKSUM", "PERSISTENT", "STATS_AUTO_RECALC",
    "STATS_PERSISTENT", "STATS_SAMPLE_PAGES", "DATA_DIRECTORY", "INDEX_DIRECTORY",
    "TABLESPACE", "STORAGE", "UNION", "INSERT_METHOD", "AUTO_INCREMENT",
    "DEFAULT", "CHARACTER", "SET", "COLLATE", "ENGINE", "AUTO_INCREMENT_OFFSET",
    "AUTO_INCREMENT_INCREMENT", "DELAY_KEY_WRITE", "INSERT_METHOD", "MAX_ROWS",
    "MIN_ROWS", "AVG_ROW_LENGTH", "PACK_KEYS", "STATS_AUTO_RECALC", "STATS_PERSISTENT",
    "STATS_SAMPLE_PAGES", "DATA_DIRECTORY", "INDEX_DIRECTORY", "TABLESPACE",
    "STORAGE", "UNION", "INSERT_METHOD", "AUTO_INCREMENT", "DEFAULT", "CHARACTER",
    "SET", "COLLATE", "ENGINE", "RAID_TYPE", "RAID_CHUNKS", "RAID_CHUNKSIZE",
    "INITIAL", "NEXT", "MINVALUE", "MAXVALUE", "START", "INCREMENT", "CACHE",
    "CYCLE", "NOCYCLE", "NOMINVALUE", "NOMAXVALUE", "NOORDER", "ORDER",
    "COMMENT", "AS", "BEFORE", "AFTER", "INSTEAD", "OF", "EACH", "ROW",
    "STATEMENT", "OLD", "NEW", "FOLLOWS", "PRECEDES", "CONDITION", "SQLSTATE",
    "SQLWARNING", "NOTFOUND", "SQLEXCEPTION", "REPLACE", "INSERT", "DELETE",
    "UPDATE", "FETCH", "CLOSE", "OPEN", "DECLARE", "HANDLER", "CONTINUE",
    "EXIT", "UNDO", "SIGNAL", "RESIGNAL", "LEAVE", "ITERATE", "LOOP",
    "REPEAT", "WHILE", "IF", "ELSEIF", "ELSE", "CASE", "WHEN", "THEN",
    "RETURN", "RETURNS", "LANGUAGE", "SQL", "NOSQL", "DETERMINISTIC", "NOT",
    "CONTAINS", "SQL", "NO", "SQL", "READS", "DATA", "MODIFIES", "SQL",
    "DATA", "SECURITY", "DEFINER", "INVOKER", "ACCESS", "COMMENT", "CHARACTER",
    "SET", "COLLATE", "DATA", "TYPE", "RESULT", "CACHE", "AUTHID", "CURRENT_USER",
    "DEFINER", "INVOKER", "SQL", "STATE", "ATOMIC", "NOT", "NULL", "LANGUAGE",
    "PARAMETER", "STYLE", "GENERAL", "SQL", "INHERIT", "TRIGGER", "EVENT",
    "SCHEDULE", "EVERY", "AT", "ENABLE", "DISABLE", "ON", "COMPLETION",
    "NOT", "PRESERVE", "DO", "SHOW", "BINLOG", "EVENTS", "LOGS", "SLAVE",
    "HOSTS", "LOGS", "MASTER", "STATUS", "ENGINES", "ENGINE", "PROCESSLIST",
    "FULL", "OPEN", "TABLES", "DATABASES", "SCHEMAS", "TABLES", "COLUMNS",
    "FIELDS", "INDEX", "KEYS", "PRIVILEGES", "GRANTS", "CREATE", "USER",
    "EVENT", "FUNCTION", "PROCEDURE", "SERVER", "LOGFILE", "TABLESPACE",
    "TRIGGER", "VIEW", "DATABASE", "SCHEMA", "TABLE", "INDEX", "CONSTRAINT",
    "DATABASES", "SCHEMAS", "TABLES", "TABLE", "COLUMNS", "FIELDS", "INDEX",
    "KEY", "CONSTRAINT", "REFERENCES", "REFERENCE", "OPTION", "OPTIONS",
    "RENAME", "TO", "AS", "LIKE", "REGEXP", "RLIKE", "MATCH", "AGAINST",
    "USING", "WITH", "ROLLUP", "CUBE", "PIVOT", "UNPIVOT", "LIMIT", "OFFSET",
    "ROWS", "FETCH", "FIRST", "NEXT", "ONLY", "TIES", "WITH", "TIES",
    "FOR", "UPDATE", "SHARE", "MODE", "NOWAIT", "SKIP", "LOCKED", "OF",
    "TABLE", "PARTITION", "PARTITIONS", "SUBPARTITION", "SUBPARTITIONS",
    "VALUES", "LESS", "THAN", "MAXVALUE", "IN", "EACH", "ROW", "STORAGE",
    "ENGINE", "COMMENT", "DATA", "INDEX", "DIRECTORY", "MIN_ROWS", "MAX_ROWS",
    "AVG_ROW_LENGTH", "PACK_KEYS", "CHECKSUM", "DELAY_KEY_WRITE", "ROW_FORMAT",
    "COMPRESSION", "BLOCK_SIZE", "PAGE_CHECKSUM", "PERSISTENT", "STATS_AUTO_RECALC",
    "STATS_PERSISTENT", "STATS_SAMPLE_PAGES", "TABLESPACE", "STORAGE", "UNION",
    "INSERT_METHOD", "AUTO_INCREMENT", "DEFAULT", "CHARACTER", "SET", "COLLATE",
    "UNIQUE", "PRIMARY", "KEY", "INDEX", "CONSTRAINT", "FOREIGN", "REFERENCES",
    "REFERENCE", "ON", "DELETE", "UPDATE", "CASCADE", "SET", "NULL", "NO",
    "ACTION", "RESTRICT", "CHECK", "COMMENT", "AS", "VISIBLE", "INVISIBLE",
    "GENERATED", "ALWAYS", "VIRTUAL", "STORED", "SIGNED", "UNSIGNED", "ZEROFILL",
}

ALL_SQL_KEYWORDS = SQL_KEYWORDS_BASE.union(DAMA_SPECIFIC_KEYWORDS)

SPECIAL_STRING_PATTERNS = [
    r"yyyy[-/\\.]mm[-/\\.]dd",
    r"YYYY[-/\\.]MM[-/\\.]DD",
    r"yy[-/\\.]mm[-/\\.]dd",
    r"YY[-/\\.]MM[-/\\.]DD",
    r"yyyy[-/\\.]MM[-/\\.]dd",
    r"YYYY[-/\\.]mm[-/\\.]DD",
    r"HH:mm:ss",
    r"HH24:MI:SS",
    r"HH:MI:SS",
    r"hh:mm:ss",
    r"HH:mm",
    r"HH24:MI",
    r"HH:MI",
    r"hh:mm",
    r"yyyy-MM-dd HH:mm:ss",
    r"YYYY-MM-DD HH24:MI:SS",
    r"yyyy-MM-dd HH:mm",
    r"YYYY-MM-DD HH24:MI",
    r"yyyy/MM/dd HH:mm:ss",
    r"YYYY/MM/DD HH24:MI:SS",
    r"yyyy.MM.dd HH:mm:ss",
    r"YYYY.MM.DD HH24:MI:SS",
    r"%Y-%m-%d",
    r"%y-%m-%d",
    r"%H:%M:%S",
    r"%H:%M",
    r"%Y-%m-%d %H:%M:%S",
    r"%Y/%m/%d",
    r"%m/%d/%Y",
    r"%d/%m/%Y",
    r"%b %d, %Y",
    r"%d-%b-%Y",
    r"Mon DD YYYY",
    r"DD Mon YYYY",
    r"FMYYYY",
    r"FMMM",
    r"FMDD",
    r"FMHH24",
    r"FMMI",
    r"FMSS",
    r"SP",
    r"TH",
    r"J",
    r"RR",
    r"RRRR",
    r"CC",
    r"SCC",
    r"WW",
    r"IW",
    r"W",
    r"Q",
    r"HH",
    r"HH12",
    r"HH24",
    r"MI",
    r"SS",
    r"SSSSS",
    r"FF",
    r"FF1",
    r"FF2",
    r"FF3",
    r"FF4",
    r"FF5",
    r"FF6",
    r"FF7",
    r"FF8",
    r"FF9",
    r"TZD",
    r"TZH",
    r"TZM",
    r"TS",
    r"TZR",
    r"AM",
    r"PM",
    r"am",
    r"pm",
    r"A.M.",
    r"P.M.",
    r"a.m.",
    r"p.m.",
    r"BC",
    r"AD",
    r"B.C.",
    r"A.D.",
    r"bc",
    r"ad",
    r"b.c.",
    r"a.d.",
    r"DAY",
    r"DY",
    r"MON",
    r"MONTH",
    r"RM",
    r"DL",
    r"DS",
    r"TS",
    r"E",
    r"EE",
    r"EEE",
    r"EEEE",
    r"Z",
    r"z",
    r"ZZZ",
    r"X",
    r"XX",
    r"XXX",
    r"u",
    r"G",
    r"GG",
    r"GGG",
    r"GGGG",
    r"w",
    r"ww",
    r"W",
    r"WW",
    r"D",
    r"DD",
    r"DDD",
    r"F",
    r"E",
    r"u",
    r"a",
    r"K",
    r"H",
    r"k",
    r"h",
    r"m",
    r"s",
    r"S",
    r"A",
    r"z",
    r"Z",
    r"X",
    r"YYYYMMDD",
    r"YYYYMM",
    r"YYMMDD",
    r"YYMM",
    r"YYYY-MM-DDTHH:mm:ss",
    r"YYYY-MM-DDTHH:mm:ssZ",
    r"YYYY-MM-DDTHH:mm:ss.SSS",
    r"YYYY-MM-DDTHH:mm:ss.SSSZ",
    r"yyyy-MM-dd'T'HH:mm:ss",
    r"yyyy-MM-dd'T'HH:mm:ssZ",
    r"yyyy-MM-dd'T'HH:mm:ss.SSS",
    r"yyyy-MM-dd'T'HH:mm:ss.SSSZ",
    r"yyyyMMddHHmmss",
    r"yyyyMMddHHmm",
    r"yyMMddHHmmss",
    r"yyMMddHHmm",
]

SPECIAL_STRING_REGEX = re.compile(
    "|".join(f"({pattern})" for pattern in SPECIAL_STRING_PATTERNS),
    re.IGNORECASE
)


class SQLAnonymizer:
    def __init__(
        self,
        exclude_list: Optional[List[str]] = None,
        dialect: str = "mysql"
    ):
        self.exclude_list = [item.strip().lower() for item in (exclude_list or [])]
        self.dialect = dialect.lower()
        self.table_mapping: OrderedDict[str, str] = OrderedDict()
        self.field_mapping: OrderedDict[str, str] = OrderedDict()
        self.table_counter = 0
        self.field_counter = 0
        
        self.keywords = self._get_keywords()
        
    RESERVED_KEYWORDS = {
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL",
        "ON", "AS", "AND", "OR", "NOT", "IN", "LIKE", "EXISTS", "BETWEEN", "IS", "NULL",
        "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL", "DISTINCT",
        "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "DROP",
        "ALTER", "ADD", "COLUMN", "CONSTRAINT", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
        "UNIQUE", "INDEX", "VIEW", "TRIGGER", "PROCEDURE", "FUNCTION", "RETURN", "CALL",
        "COMMIT", "ROLLBACK", "SAVEPOINT", "TRANSACTION", "BEGIN", "END", "IF", "ELSE",
        "CASE", "WHEN", "THEN", "ELSEIF", "WHILE", "LOOP", "FOR", "CURSOR", "OPEN",
        "CLOSE", "FETCH", "DECLARE", "TRUE", "FALSE", "ASC", "DESC",
        "DATE_FORMAT", "TIME_FORMAT", "STR_TO_DATE", "TO_DATE", "TO_CHAR", "TO_NUMBER",
        "COALESCE", "IFNULL", "NULLIF", "NVL", "NVL2", "DECODE", "GREATEST", "LEAST",
        "CAST", "CONVERT", "ROUND", "TRUNC", "TRUNCATE", "FLOOR", "CEIL", "CEILING",
        "ABS", "MOD", "SIGN", "POW", "POWER", "SQRT", "EXP", "LN", "LOG", "LOG2", "LOG10",
        "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN", "ATAN2", "SINH", "COSH", "TANH",
        "RADIANS", "DEGREES", "PI", "RAND", "RANDOM", "UUID", "UUID_SHORT", "MD5", "SHA1", "SHA2",
        "CONCAT", "CONCAT_WS", "SUBSTRING", "SUBSTR", "MID", "LEFT", "RIGHT", "LENGTH",
        "CHAR_LENGTH", "CHARACTER_LENGTH", "BIT_LENGTH", "LOWER", "UPPER", "INITCAP",
        "TRIM", "LTRIM", "RTRIM", "LPAD", "RPAD", "REPLACE", "TRANSLATE", "REVERSE",
        "INSTR", "LOCATE", "POSITION", "STRCMP", "SOUNDEX", "SUBSTRING_INDEX",
        "NOW", "CURDATE", "CURRENT_DATE", "CURTIME", "CURRENT_TIME", "SYSDATE",
        "CURRENT_TIMESTAMP", "LOCALTIME", "LOCALTIMESTAMP",
        "YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND", "MICROSECOND",
        "DAYOFYEAR", "DAYOFMONTH", "DAYOFWEEK", "WEEKDAY", "WEEK", "WEEKOFYEAR", "YEARWEEK",
        "QUARTER", "MONTHNAME", "DAYNAME",
        "DATE_ADD", "DATE_SUB", "ADDDATE", "SUBDATE", "ADDTIME", "SUBTIME",
        "DATEDIFF", "TIMEDIFF", "TIMESTAMPADD", "TIMESTAMPDIFF",
        "EXTRACT", "PERIOD_ADD", "PERIOD_DIFF", "TO_DAYS", "FROM_DAYS",
        "MAKEDATE", "MAKETIME", "SEC_TO_TIME", "TIME_TO_SEC",
        "FORMAT", "INET_ATON", "INET_NTOA", "INET6_ATON", "INET6_NTOA",
        "COALESCE", "IFNULL", "NULLIF", "GREATEST", "LEAST", "INTERVAL",
        "LAST_INSERT_ID", "ROW_COUNT", "FOUND_ROWS", "CONNECTION_ID",
        "CURRENT_USER", "SESSION_USER", "SYSTEM_USER", "USER", "DATABASE", "SCHEMA",
        "VERSION", "CHARSET", "COLLATION", "COERCIBILITY",
        "CHAR", "ASCII", "ORD", "QUOTE", "BIT_COUNT",
        "GET_LOCK", "RELEASE_LOCK", "IS_FREE_LOCK", "IS_USED_LOCK",
        "SLEEP", "BENCHMARK", "LAST_DAY",
        "MATCH", "AGAINST", "BOOLEAN", "MODE",
        "ELT", "FIELD", "FIND_IN_SET", "MAKE_SET", "SPACE",
        "REGEXP", "RLIKE", "BINARY", "MATCH",
        "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END",
        "COALESCE", "NULLIF", "NVL", "NVL2", "DECODE",
        "SIGN", "ABS", "MOD", "ROUND", "TRUNC", "TRUNCATE",
        "CEIL", "CEILING", "FLOOR", "RAND", "RANDOM",
        "LOG", "LN", "LOG2", "LOG10", "EXP", "POW", "POWER", "SQRT",
        "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN", "ATAN2",
        "BIT_AND", "BIT_OR", "BIT_XOR", "BIT_COUNT",
        "GROUP_CONCAT", "COUNT", "SUM", "AVG", "MIN", "MAX",
        "STD", "STDDEV", "STDDEV_POP", "STDDEV_SAMP",
        "VARIANCE", "VAR_POP", "VAR_SAMP",
        "BIT_AND", "BIT_OR", "BIT_XOR",
        "JSON_EXTRACT", "JSON_UNQUOTE", "JSON_VALID",
        "JSON_CONTAINS", "JSON_CONTAINS_PATH",
        "JSON_KEYS", "JSON_LENGTH", "JSON_DEPTH",
        "JSON_TYPE", "JSON_PRETTY", "JSON_QUOTE",
        "JSON_ARRAY", "JSON_OBJECT", "JSON_MERGE",
        "JSON_SET", "JSON_INSERT", "JSON_REPLACE",
        "JSON_REMOVE", "JSON_ARRAY_APPEND", "JSON_ARRAY_INSERT",
        "JSON_SEARCH", "JSON_CONTAINS", "JSON_OVERLAPS",
        "XML_EXTRACTVALUE", "XML_UPDATE",
        "ST_ASTEXT", "ST_ASBINARY", "ST_GEOMFROMTEXT", "ST_GEOMFROMWKB",
        "ST_X", "ST_Y", "ST_DISTANCE", "ST_WITHIN", "ST_CONTAINS",
        "ST_INTERSECTS", "ST_DISJOINT", "ST_TOUCHES", "ST_OVERLAPS",
        "ST_CROSSES", "ST_EQUALS", "ST_LENGTH", "ST_AREA",
        "ST_CENTROID", "ST_BOUNDARY", "ST_BUFFER", "ST_CONVEXHULL",
        "ST_DIFFERENCE", "ST_INTERSECTION", "ST_SYMDIFFERENCE", "ST_UNION",
        "ST_SRID", "ST_GEOMETRYTYPE", "ST_DIMENSION",
        "ST_ENVELOPE", "ST_ISVALID", "ST_ISSIMPLE", "ST_ISCLOSED",
        "ST_ISRING", "ST_STARTPOINT", "ST_ENDPOINT",
        "ST_NUMGEOMETRIES", "ST_GEOMETRYN", "ST_NUMPOINTS", "ST_POINTN",
        "ST_EXTERIORRING", "ST_NUMINTERIORRINGS", "ST_INTERIORRINGN",
    }
    
    def _get_keywords(self) -> Set[str]:
        return self.RESERVED_KEYWORDS
    
    def _is_keyword(self, token: str) -> bool:
        return token.upper() in self.keywords
    
    def _should_exclude(self, name: str) -> bool:
        name_lower = name.lower()
        for exclude in self.exclude_list:
            if exclude in name_lower:
                return True
        return False
    
    def _is_special_string(self, text: str) -> bool:
        cleaned = text.strip("'\"`")
        if SPECIAL_STRING_REGEX.search(cleaned):
            return True
        date_patterns = [
            r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$",
            r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$",
            r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{1,2}(:\d{1,2})?$",
        ]
        for pattern in date_patterns:
            if re.match(pattern, cleaned):
                return True
        return False
    
    def _get_table_alias(self, original: str) -> str:
        original_clean = original.strip("`\"'")
        
        if self._should_exclude(original_clean):
            return original
        
        if original_clean in self.table_mapping:
            return self.table_mapping[original_clean]
        
        if self._is_keyword(original_clean):
            return original
        
        self.table_counter += 1
        alias = f"table_{self.table_counter:03d}"
        self.table_mapping[original_clean] = alias
        return alias
    
    def _get_field_alias(self, original: str) -> str:
        original_clean = original.strip("`\"'")
        
        if self._should_exclude(original_clean):
            return original
        
        if original_clean in self.field_mapping:
            return self.field_mapping[original_clean]
        
        if self._is_keyword(original_clean):
            return original
        
        self.field_counter += 1
        alias = f"field_{self.field_counter:03d}"
        self.field_mapping[original_clean] = alias
        return alias
    
    def _split_tokens(self, sql: str) -> List[Tuple[str, str]]:
        tokens = []
        
        patterns = [
            ("STRING", r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`[^`]*`)"),
            ("NUMBER", r"\b\d+\.?\d*([eE][+-]?\d+)?\b"),
            ("COMMENT", r"--.*?(?=\n|$)|/\*[\s\S]*?\*/"),
            ("OPERATOR", r"(<=|>=|<>|!=|==|\|\||\*\*|\+|-|\*|/|%|\||&|\^|~|<<|>>)"),
            ("PUNCTUATION", r"([(),;.:])"),
            ("WHITESPACE", r"(\s+)"),
            ("IDENTIFIER", r"([a-zA-Z_][a-zA-Z0-9_$@#]*)"),
        ]
        
        combined_pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in patterns)
        regex = re.compile(combined_pattern, re.MULTILINE)
        
        pos = 0
        while pos < len(sql):
            match = regex.match(sql, pos)
            if match:
                token_type = match.lastgroup
                token_value = match.group()
                tokens.append((token_type, token_value))
                pos = match.end()
            else:
                tokens.append(("UNKNOWN", sql[pos]))
                pos += 1
        
        return tokens
    
    def _is_table_context(self, tokens: List[Tuple[str, str]], index: int) -> bool:
        table_context_keywords = {
            "FROM", "JOIN", "INNER", "LEFT", "RIGHT", "FULL", "OUTER",
            "INTO", "UPDATE", "TABLE", "USING", "REFERENCES", "AS"
        }
        
        for i in range(index - 1, max(-1, index - 5), -1):
            token_type, token_value = tokens[i]
            if token_type == "IDENTIFIER":
                if token_value.upper() in table_context_keywords:
                    return True
            elif token_type == "WHITESPACE" or token_type == "COMMENT":
                continue
            else:
                break
        
        for i in range(index + 1, min(len(tokens), index + 3)):
            token_type, token_value = tokens[i]
            if token_type == "IDENTIFIER":
                if token_value.upper() in {"AS", "ON", "WHERE", "USING", "JOIN", "(", ")"}:
                    return True
            elif token_type == "WHITESPACE":
                continue
            else:
                break
        
        return False
    
    def _is_field_context(self, tokens: List[Tuple[str, str]], index: int) -> bool:
        token_type, token_value = tokens[index]
        
        if self._is_keyword(token_value):
            return False
        
        if index > 0:
            prev_type, prev_value = tokens[index - 1]
            if prev_value == ".":
                return True
            if prev_value.upper() in {"SELECT", "WHERE", "HAVING", "ON", "AND", "OR", "NOT", "IN", "=", "!=", "<", ">", "<=", ">=", "<>", "+-*/%"}:
                return True
        
        if index < len(tokens) - 1:
            next_type, next_value = tokens[index + 1]
            if next_value in {".", "=", ",", ")", "AS", "AND", "OR", "IN", "LIKE", "BETWEEN"}:
                return True
        
        return True
    
    def _scan_table_names(self, tokens: List[Tuple[str, str]]) -> Set[str]:
        """
        扫描所有表名：
        - FROM 后面的标识符
        - JOIN 后面的标识符
        - INTO 后面的标识符
        - UPDATE 后面的标识符
        - TABLE 后面的标识符
        """
        table_names = set()
        table_context_keywords = {
            "FROM", "JOIN", "INNER", "LEFT", "RIGHT", "FULL", "OUTER",
            "INTO", "UPDATE", "TABLE"
        }
        
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == "IDENTIFIER" and token_value.upper() in table_context_keywords:
                j = i + 1
                while j < len(tokens):
                    next_type, next_value = tokens[j]
                    if next_type == "WHITESPACE" or next_type == "COMMENT":
                        j += 1
                    elif next_type == "IDENTIFIER" and not self._is_keyword(next_value):
                        table_names.add(next_value.strip("`\"'"))
                        break
                    else:
                        break
                    j += 1
            
            i += 1
        
        return table_names
    
    def _scan_table_aliases(self, tokens: List[Tuple[str, str]], table_names: Set[str]) -> Dict[str, str]:
        """
        扫描表别名：表名后面的标识符可能是别名
        例如：FROM users u -> u 是 users 的别名
        """
        alias_to_table = {}
        
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == "IDENTIFIER":
                token_clean = token_value.strip("`\"'")
                if token_clean in table_names:
                    j = i + 1
                    while j < len(tokens):
                        next_type, next_value = tokens[j]
                        if next_type == "WHITESPACE" or next_type == "COMMENT":
                            j += 1
                        elif next_type == "IDENTIFIER" and not self._is_keyword(next_value):
                            alias_clean = next_value.strip("`\"'")
                            if alias_clean not in table_names and not self._should_exclude(alias_clean):
                                alias_to_table[alias_clean] = token_clean
                            break
                        else:
                            break
                        j += 1
            
            i += 1
        
        return alias_to_table
    
    def _is_field_context_at(self, tokens: List[Tuple[str, str]], index: int, 
                               table_names: Set[str], alias_to_table: Dict[str, str]) -> bool:
        """
        判断当前位置是否是字段名上下文
        """
        if index > 0:
            prev_type, prev_value = tokens[index - 1]
            if prev_value == ".":
                return True
        
        field_context_keywords = {
            "SELECT", "WHERE", "HAVING", "ON", "AND", "OR", "NOT",
            "ORDER", "GROUP", "BY", "SET", "VALUES"
        }
        
        for i in range(index - 1, max(-1, index - 10), -1):
            token_type, token_value = tokens[i]
            if token_type == "IDENTIFIER":
                if token_value.upper() in field_context_keywords:
                    return True
                if token_value.upper() == "AS":
                    continue
            elif token_type == "WHITESPACE" or token_type == "COMMENT":
                continue
            elif token_type == "PUNCTUATION" and token_value in {",", "(", ")"}:
                continue
            elif token_type == "OPERATOR":
                return True
            else:
                break
        
        for i in range(index + 1, min(len(tokens), index + 5)):
            token_type, token_value = tokens[i]
            if token_type == "WHITESPACE" or token_type == "COMMENT":
                continue
            elif token_type == "PUNCTUATION" and token_value in {",", ")", "("}:
                continue
            elif token_type == "OPERATOR":
                return True
            elif token_type == "IDENTIFIER" and token_value.upper() in {"AS", "FROM", "WHERE", "ON", "AND", "OR", "IN", "LIKE", "BETWEEN"}:
                return True
            else:
                break
        
        return False
    
    def anonymize(self, sql: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
        self.table_mapping.clear()
        self.field_mapping.clear()
        self.table_counter = 0
        self.field_counter = 0
        
        tokens = self._split_tokens(sql)
        
        table_names = self._scan_table_names(tokens)
        alias_to_table = self._scan_table_aliases(tokens, table_names)
        
        result = []
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == "STRING":
                result.append(token_value)
            
            elif token_type == "IDENTIFIER":
                if self._is_keyword(token_value):
                    result.append(token_value)
                else:
                    token_clean = token_value.strip("`\"'")
                    
                    if "." in token_value and not token_value.startswith(".") and not token_value.endswith("."):
                        parts = token_value.split(".")
                        anonymized_parts = []
                        for j, part in enumerate(parts):
                            part_clean = part.strip("`\"'")
                            
                            if part_clean in table_names:
                                anonymized_parts.append(self._get_table_alias(part))
                            elif part_clean in alias_to_table:
                                original_table = alias_to_table[part_clean]
                                anonymized_parts.append(self._get_table_alias(part))
                            elif not self._is_keyword(part):
                                is_field = False
                                if j > 0:
                                    is_field = True
                                else:
                                    is_field = self._is_field_context_at(tokens, i, table_names, alias_to_table)
                                
                                if is_field:
                                    anonymized_parts.append(self._get_field_alias(part))
                                elif part_clean in table_names:
                                    anonymized_parts.append(self._get_table_alias(part))
                                else:
                                    is_table_candidate = (
                                        self._is_table_context(tokens, i) or
                                        part_clean in table_names
                                    )
                                    if is_table_candidate:
                                        anonymized_parts.append(self._get_table_alias(part))
                                    else:
                                        anonymized_parts.append(self._get_field_alias(part))
                            else:
                                anonymized_parts.append(part)
                        result.append(".".join(anonymized_parts))
                    
                    elif token_clean in table_names:
                        result.append(self._get_table_alias(token_value))
                    
                    elif token_clean in alias_to_table:
                        result.append(self._get_table_alias(token_value))
                    
                    elif self._is_table_context(tokens, i):
                        result.append(self._get_table_alias(token_value))
                    
                    elif self._is_field_context(tokens, i):
                        result.append(self._get_field_alias(token_value))
                    
                    else:
                        result.append(self._get_field_alias(token_value))
            else:
                result.append(token_value)
            
            i += 1
        
        anonymized_sql = "".join(result)
        
        mapping = {
            "tables": {v: k for k, v in self.table_mapping.items()},
            "fields": {v: k for k, v in self.field_mapping.items()},
        }
        
        return anonymized_sql, mapping
    
    def deanonymize(
        self, 
        sql: str, 
        mapping: Dict[str, Dict[str, str]]
    ) -> str:
        """
        反向匿名化：根据编码字典将匿名化后的脚本还原为原始脚本
        
        Args:
            sql: 匿名化后的 SQL 脚本
            mapping: 编码字典，格式为 {"tables": {"table_001": "users"}, "fields": {"field_001": "user_id"}}
        
        Returns:
            还原后的 SQL 脚本
        """
        if not mapping:
            return sql
        
        table_mapping = mapping.get("tables", {})
        field_mapping = mapping.get("fields", {})
        
        tokens = self._split_tokens(sql)
        result = []
        
        table_names_set = set(table_mapping.keys())
        field_names_set = set(field_mapping.keys())
        
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == "STRING":
                result.append(token_value)
            
            elif token_type == "IDENTIFIER":
                if self._is_keyword(token_value):
                    result.append(token_value)
                else:
                    token_clean = token_value.strip("`\"'")
                    
                    if "." in token_value and not token_value.startswith(".") and not token_value.endswith("."):
                        parts = token_value.split(".")
                        deanonymized_parts = []
                        for part in parts:
                            part_clean = part.strip("`\"'")
                            
                            if part_clean in table_mapping:
                                deanonymized_parts.append(table_mapping[part_clean])
                            elif part_clean in field_mapping:
                                deanonymized_parts.append(field_mapping[part_clean])
                            elif not self._is_keyword(part):
                                if part_clean in table_names_set:
                                    deanonymized_parts.append(table_mapping[part_clean])
                                elif part_clean in field_names_set:
                                    deanonymized_parts.append(field_mapping[part_clean])
                                else:
                                    deanonymized_parts.append(part)
                            else:
                                deanonymized_parts.append(part)
                        result.append(".".join(deanonymized_parts))
                    
                    elif token_clean in table_mapping:
                        result.append(table_mapping[token_clean])
                    
                    elif token_clean in field_mapping:
                        result.append(field_mapping[token_clean])
                    
                    else:
                        result.append(token_value)
            else:
                result.append(token_value)
            
            i += 1
        
        deanonymized_sql = "".join(result)
        
        return deanonymized_sql


def remove_comments_and_empty_lines(sql: str) -> str:
    """
    从 SQL 脚本中删除注释和空行
    
    Args:
        sql: 原始 SQL 脚本
    
    Returns:
        清理后的 SQL 脚本
    """
    lines = sql.split('\n')
    cleaned_lines = []
    
    in_block_comment = False
    
    for line in lines:
        stripped_line = line.strip()
        
        if not stripped_line:
            continue
        
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
                _, after_comment = line.split("*/", 1)
                if after_comment.strip():
                    cleaned_lines.append(after_comment.rstrip())
            continue
        
        while "--" in line:
            idx = line.find("--")
            if idx >= 0:
                line = line[:idx]
        
        while "/*" in line:
            idx = line.find("/*")
            end_idx = line.find("*/", idx)
            
            if end_idx >= 0:
                line = line[:idx] + line[end_idx + 2:]
            else:
                line = line[:idx]
                in_block_comment = True
                break
        
        stripped_line = line.strip()
        if stripped_line:
            cleaned_lines.append(line.rstrip())
    
    return '\n'.join(cleaned_lines)


def anonymize_sql(
    sql: str,
    exclude_list: Optional[List[str]] = None,
    dialect: str = "mysql",
    remove_comments: bool = True
) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    匿名化 SQL 脚本
    
    Args:
        sql: 原始 SQL 脚本
        exclude_list: 排除列表，包含这些字符串的表名或字段名不会被匿名化
        dialect: 数据库方言
        remove_comments: 是否删除注释和空行
    
    Returns:
        (匿名化后的 SQL 脚本, 编码字典)
    """
    if remove_comments:
        sql = remove_comments_and_empty_lines(sql)
    
    anonymizer = SQLAnonymizer(exclude_list=exclude_list, dialect=dialect)
    return anonymizer.anonymize(sql)


def deanonymize_sql(
    sql: str,
    mapping: Dict[str, Dict[str, str]],
    dialect: str = "mysql"
) -> str:
    """
    反向匿名化 SQL 脚本
    
    Args:
        sql: 匿名化后的 SQL 脚本
        mapping: 编码字典
        dialect: 数据库方言
    
    Returns:
        还原后的 SQL 脚本
    """
    anonymizer = SQLAnonymizer(dialect=dialect)
    return anonymizer.deanonymize(sql, mapping)