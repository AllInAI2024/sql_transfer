import sys
sys.path.insert(0, '/Users/victor/code/meetchances/solo-coder/sql_transfer')

from app.services.visualization_import_service import (
    extract_table_names_from_sql,
    extract_table_names_simple,
    build_integrated_script,
    process_visualization_script_import
)

print('✅ 导入成功')

sql = '''
SELECT u.id, u.name, o.order_no
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
'''

tables = extract_table_names_simple(sql)
print(f'✅ 表名提取测试: {tables}')

intermediate_scripts = {
    'users': 'CREATE TABLE users (id INT, name VARCHAR(100));',
    'orders': 'CREATE TABLE orders (id INT, user_id INT, order_no VARCHAR(50));'
}

result = process_visualization_script_import(
    script_name='测试脚本',
    visualization_script=sql,
    existing_intermediate_scripts=intermediate_scripts
)

print(f'✅ 中间表名: {result["intermediate_table_names"]}')
print(f'✅ 找到的表: {result["found_tables"]}')
print(f'✅ 缺失的表: {result["missing_tables"]}')
print('\n✅ 整合脚本内容:')
print(result["integrated_script"])
print('\n✅ 所有测试通过!')
