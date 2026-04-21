import re
from typing import List, Set, Dict, Tuple, Optional


SQL_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL",
    "ON", "AS", "AND", "OR", "NOT", "IN", "LIKE", "EXISTS", "BETWEEN", "IS", "NULL",
    "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL", "DISTINCT",
    "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "DROP",
    "ALTER", "ADD", "COLUMN", "CONSTRAINT", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
    "UNIQUE", "INDEX", "VIEW", "TRIGGER", "PROCEDURE", "FUNCTION", "RETURN", "CALL",
    "COMMIT", "ROLLBACK", "SAVEPOINT", "TRANSACTION", "BEGIN", "END", "IF", "ELSE",
    "CASE", "WHEN", "THEN", "ELSEIF", "WHILE", "LOOP", "FOR", "CURSOR", "OPEN",
    "CLOSE", "FETCH", "DECLARE", "TRUE", "FALSE", "ASC", "DESC", "TOP", "PERCENT",
    "TIES", "ONLY", "FIRST", "NEXT", "ROW", "ROWS", "OVER", "PARTITION",
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
}


def tokenize_sql(sql: str) -> List[Tuple[str, str]]:
    """
    将 SQL 分解为 token
    返回: [(token类型, token值), ...]
    """
    string_pattern = r"""'(?:''|[^'])*'|"(?:""|[^"])*"|`(?:``|[^`])*`"""
    number_pattern = r"\b\d+\.?\d*\b"
    identifier_pattern = r"[a-zA-Z_][a-zA-Z0-9_]*"
    operator_pattern = r"[+\-*/<>=!~&|^%]+"
    punctuation_pattern = r"[(),.;:]"
    whitespace_pattern = r"\s+"
    comment_pattern = r"--.*$|/\*[\s\S]*?\*/"
    
    combined_pattern = f"({string_pattern})|({number_pattern})|({identifier_pattern})|({operator_pattern})|({punctuation_pattern})|({whitespace_pattern})|({comment_pattern})"
    
    tokens = []
    for match in re.finditer(combined_pattern, sql, re.MULTILINE):
        if match.group(1):
            tokens.append(('STRING', match.group(1)))
        elif match.group(2):
            tokens.append(('NUMBER', match.group(2)))
        elif match.group(3):
            tokens.append(('IDENTIFIER', match.group(3)))
        elif match.group(4):
            tokens.append(('OPERATOR', match.group(4)))
        elif match.group(5):
            tokens.append(('PUNCTUATION', match.group(5)))
        elif match.group(6):
            tokens.append(('WHITESPACE', match.group(6)))
        elif match.group(7):
            tokens.append(('COMMENT', match.group(7)))
    
    return tokens


def extract_cte_table_names(sql: str) -> Set[str]:
    """
    从 SQL 中提取 WITH 子句定义的 CTE（Common Table Expression）表名
    
    这些是临时表，不是真正的中间表，不应该被识别为需要查找的中间表。
    
    WITH 子句的格式：
    WITH cte1 AS (SELECT ...),
         cte2 AS (SELECT ...)
    SELECT * FROM cte1
    """
    tokens = tokenize_sql(sql)
    cte_names = set()
    
    tokens_upper = [(t, v.upper() if t == 'IDENTIFIER' else v) for t, v in tokens]
    
    i = 0
    while i < len(tokens_upper):
        token_type, token_value = tokens_upper[i]
        
        if token_type == 'IDENTIFIER' and token_value == 'WITH':
            j = i + 1
            in_with_clause = True
            
            while j < len(tokens_upper) and in_with_clause:
                j_type, j_value = tokens_upper[j]
                
                if j_type in ('WHITESPACE', 'COMMENT'):
                    j += 1
                    continue
                
                if j_type == 'IDENTIFIER' and j_value not in SQL_KEYWORDS:
                    cte_name = tokens[j][1].lower()
                    cte_names.add(cte_name)
                    
                    k = j + 1
                    found_as = False
                    found_open_paren = False
                    paren_balance = 0
                    
                    while k < len(tokens_upper):
                        k_type, k_value = tokens_upper[k]
                        
                        if k_type in ('WHITESPACE', 'COMMENT'):
                            k += 1
                            continue
                        
                        if k_type == 'IDENTIFIER' and k_value == 'AS' and not found_as:
                            found_as = True
                            k += 1
                            continue
                        
                        if k_type == 'PUNCTUATION' and k_value == '(' and found_as and not found_open_paren:
                            found_open_paren = True
                            paren_balance = 1
                            k += 1
                            continue
                        
                        if found_open_paren and paren_balance > 0:
                            if k_type == 'PUNCTUATION':
                                if k_value == '(':
                                    paren_balance += 1
                                elif k_value == ')':
                                    paren_balance -= 1
                                    if paren_balance == 0:
                                        k += 1
                                        while k < len(tokens_upper):
                                            next_type, next_value = tokens_upper[k]
                                            if next_type in ('WHITESPACE', 'COMMENT'):
                                                k += 1
                                                continue
                                            if next_type == 'PUNCTUATION' and next_value == ',':
                                                j = k + 1
                                                break
                                            if next_type == 'IDENTIFIER' and next_value in {
                                                'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH'
                                            }:
                                                in_with_clause = False
                                                j = k
                                                break
                                            j = k
                                            in_with_clause = False
                                            break
                                        break
                            k += 1
                            continue
                        
                        break
                    
                    if paren_balance == 0 and found_open_paren:
                        continue
                    else:
                        in_with_clause = False
                        j = k
                        continue
                
                if j_type == 'IDENTIFIER' and j_value in {
                    'SELECT', 'INSERT', 'UPDATE', 'DELETE'
                }:
                    in_with_clause = False
                    break
                
                j += 1
        
        i += 1
    
    return cte_names


def extract_table_names_from_sql(sql: str) -> Set[str]:
    """
    从 SQL 中提取所有表名（包括 FROM 和 JOIN 子句后的表名）
    排除 WITH 子句定义的 CTE 临时表
    
    识别逻辑：
    1. 先识别 WITH 子句中的 CTE 表名
    2. 再识别 FROM/JOIN 后的表名
    3. 排除 CTE 表名
    """
    cte_names = extract_cte_table_names(sql)
    
    tokens = tokenize_sql(sql)
    
    table_names = set()
    
    tokens_upper = [(t, v.upper() if t == 'IDENTIFIER' else v) for t, v in tokens]
    
    table_context_keywords = {
        'FROM',
        'JOIN',
        'LEFT',
        'RIGHT',
        'INNER',
        'FULL',
        'OUTER',
        'CROSS',
        'NATURAL',
    }
    
    i = 0
    while i < len(tokens_upper):
        token_type, token_value = tokens_upper[i]
        
        if token_type == 'IDENTIFIER' and token_value in table_context_keywords:
            context_keywords = []
            j = i
            while j < len(tokens_upper) and tokens_upper[j][0] == 'IDENTIFIER' and tokens_upper[j][1] in table_context_keywords:
                context_keywords.append(tokens_upper[j][1])
                j += 1
            
            if 'FROM' in context_keywords or 'JOIN' in context_keywords:
                while j < len(tokens_upper):
                    next_type, next_value = tokens_upper[j]
                    
                    if next_type == 'WHITESPACE' or next_type == 'COMMENT':
                        j += 1
                        continue
                    
                    if next_type == 'IDENTIFIER' and next_value not in SQL_KEYWORDS:
                        table_name_lower = tokens[j][1].lower()
                        
                        if table_name_lower not in cte_names:
                            table_names.add(table_name_lower)
                        
                        k = j + 1
                        while k < len(tokens_upper):
                            k_type, k_value = tokens_upper[k]
                            if k_type == 'WHITESPACE' or k_type == 'COMMENT':
                                k += 1
                                continue
                            if k_type == 'IDENTIFIER' and k_value == 'AS':
                                k += 1
                                while k < len(tokens_upper) and tokens_upper[k][0] in ('WHITESPACE', 'COMMENT'):
                                    k += 1
                                break
                            if k_type == 'IDENTIFIER' and k_value not in SQL_KEYWORDS:
                                break
                            if k_type == 'PUNCTUATION' and k_value in (',', ')', ';', '('):
                                break
                            if k_type == 'IDENTIFIER' and k_value in {'ON', 'WHERE', 'GROUP', 'ORDER', 'LIMIT', 'UNION', 'HAVING', 'WITH'}:
                                break
                            k += 1
                        break
                    
                    if next_type == 'PUNCTUATION' and next_value == '(':
                        break
                    
                    if next_type == 'IDENTIFIER' and next_value in {'WHERE', 'GROUP', 'ORDER', 'LIMIT', 'UNION', 'HAVING', 'WITH', 'ON'}:
                        break
                    
                    break
            
            i = j - 1
        
        i += 1
    
    return table_names


def extract_table_names_simple(sql: str) -> Set[str]:
    """
    简化版的表名提取，用于快速识别
    排除 WITH 子句定义的 CTE 临时表
    """
    cte_names = extract_cte_table_names(sql)
    
    table_names = set()
    
    patterns = [
        r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bLEFT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bRIGHT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bINNER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bFULL\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bCROSS\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"\bNATURAL\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
    ]
    
    sql_upper = sql.upper()
    
    for pattern in patterns:
        matches = re.finditer(pattern, sql_upper, re.IGNORECASE)
        for match in matches:
            table_name = match.group(1)
            if table_name:
                table_name_lower = table_name.lower()
                if table_name_lower not in cte_names and table_name.upper() not in SQL_KEYWORDS:
                    table_names.add(table_name_lower)
    
    advanced_tables = extract_table_names_from_sql(sql)
    table_names.update(advanced_tables)
    
    return table_names


def build_integrated_script(
    intermediate_scripts: Dict[str, str],
    visualization_script: str,
    table_names: Set[str]
) -> str:
    """
    构建整合脚本
    
    格式：
    【中间表脚本】：
    中间表脚本内容
    【可视化脚本】：
    可视化脚本内容
    """
    result = []
    
    if intermediate_scripts and table_names:
        result.append("【中间表脚本】：")
        for table_name in sorted(table_names):
            if table_name in intermediate_scripts:
                result.append(f"\n-- 中间表: {table_name}")
                result.append(intermediate_scripts[table_name])
                result.append("")
    
    result.append("【可视化脚本】：")
    result.append("\n" + visualization_script)
    
    return "\n".join(result)


def process_visualization_script_import(
    script_name: str,
    visualization_script: str,
    existing_intermediate_scripts: Dict[str, str]
) -> Dict:
    """
    处理可视化脚本导入
    
    步骤：
    1. 从可视化脚本中提取中间表名（排除 CTE 临时表）
    2. 查找对应的中间表脚本
    3. 构建整合脚本
    4. 返回处理结果
    
    返回：
    {
        'intermediate_table_names': 'table1,table2',
        'integrated_script': '整合后的脚本',
        'found_tables': ['table1'],
        'missing_tables': ['table2'],
        'cte_tables': ['data_new']  # CTE 临时表，已排除
    }
    """
    cte_names = extract_cte_table_names(visualization_script)
    
    table_names = extract_table_names_simple(visualization_script)
    
    found_tables = []
    missing_tables = []
    intermediate_scripts_dict = {}
    
    for table_name in table_names:
        if table_name in existing_intermediate_scripts:
            found_tables.append(table_name)
            intermediate_scripts_dict[table_name] = existing_intermediate_scripts[table_name]
        else:
            upper_table_name = table_name.upper()
            lower_table_name = table_name.lower()
            found = False
            
            for key in existing_intermediate_scripts:
                if key.upper() == upper_table_name or key.lower() == lower_table_name:
                    found_tables.append(key)
                    intermediate_scripts_dict[key] = existing_intermediate_scripts[key]
                    found = True
                    break
            
            if not found:
                missing_tables.append(table_name)
    
    integrated_script = build_integrated_script(
        intermediate_scripts_dict,
        visualization_script,
        set(found_tables)
    )
    
    intermediate_table_names = ','.join(sorted(found_tables)) if found_tables else None
    
    return {
        'intermediate_table_names': intermediate_table_names,
        'integrated_script': integrated_script,
        'found_tables': found_tables,
        'missing_tables': missing_tables,
        'all_tables': list(table_names),
        'cte_tables': list(cte_names)
    }
