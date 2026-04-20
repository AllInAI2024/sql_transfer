#!/usr/bin/env python3
"""
测试 SQL 匿名化功能
"""

from app.services.anonymization_service import anonymize_sql, deanonymize_sql, remove_comments_and_empty_lines


def test_basic_select():
    """测试基本的 SELECT 语句"""
    test_sql = """
SELECT user_id, user_name, email, create_date
FROM users
WHERE create_date >= '2024-01-01'
  AND status = 1
"""
    result, mapping = anonymize_sql(test_sql, exclude_list=['date', 'time'])
    
    print("=" * 60)
    print("测试 1: 基本 SELECT 语句")
    print("=" * 60)
    print("原始 SQL:")
    print(test_sql)
    print("\n匿名化后:")
    print(result)
    print("\n映射表:")
    print(mapping)
    
    assert 'table_001' in result
    assert 'field_001' in result
    assert 'field_002' in result
    assert 'field_003' in result
    assert 'create_date' in result
    assert 'users' not in result
    assert 'user_id' not in result
    
    print("\n✓ 测试 1 通过!")
    return True


def test_complex_join():
    """测试带 JOIN 的复杂查询"""
    test_sql = """
SELECT 
    u.user_id,
    u.user_name,
    o.order_id,
    o.order_date,
    p.product_name,
    od.quantity,
    od.price
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id
INNER JOIN order_details od ON o.order_id = od.order_id
INNER JOIN products p ON od.product_id = p.product_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND o.status = 'completed'
ORDER BY o.order_date DESC
LIMIT 100
"""
    result, mapping = anonymize_sql(test_sql, exclude_list=['date', 'time'])
    
    print("\n" + "=" * 60)
    print("测试 2: 带 JOIN 的复杂查询")
    print("=" * 60)
    print("原始 SQL:")
    print(test_sql)
    print("\n匿名化后:")
    print(result)
    print("\n映射表:")
    print(mapping)
    
    assert 'INNER JOIN' in result
    assert 'ON' in result
    assert 'ORDER BY' in result
    assert 'LIMIT' in result
    assert 'BETWEEN' in result
    assert 'AND' in result
    
    print("\n✓ 测试 2 通过!")
    return True


def test_date_format_functions():
    """测试带日期格式函数的查询"""
    test_sql = """
SELECT 
    DATE_FORMAT(create_time, '%Y-%m-%d') as create_date,
    DATE_FORMAT(create_time, '%H:%i:%s') as create_time,
    TO_CHAR(sysdate, 'YYYY-MM-DD HH24:MI:SS')
FROM log_table
WHERE create_time >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
"""
    result, mapping = anonymize_sql(test_sql, exclude_list=['date', 'time'])
    
    print("\n" + "=" * 60)
    print("测试 3: 带日期格式函数的查询")
    print("=" * 60)
    print("原始 SQL:")
    print(test_sql)
    print("\n匿名化后:")
    print(result)
    print("\n映射表:")
    print(mapping)
    
    assert "'%Y-%m-%d'" in result
    assert "'YYYY-MM-DD'" in result
    assert "'YYYY-MM-DD HH24:MI:SS'" in result
    assert "'2024-01-01'" in result
    assert 'DATE_FORMAT' in result
    assert 'TO_CHAR' in result
    assert 'TO_DATE' in result
    assert 'log_table' not in result
    
    print("\n✓ 测试 3 通过!")
    return True


def test_exclude_list():
    """测试排除列表功能"""
    test_sql = """
SELECT id, name, port_number, server_port, create_date, update_time
FROM port_config
WHERE port_number > 1000
  AND status = 'active'
"""
    
    result1, mapping1 = anonymize_sql(test_sql, exclude_list=['port', 'date', 'time'])
    
    print("\n" + "=" * 60)
    print("测试 4: 排除列表功能")
    print("=" * 60)
    print("原始 SQL:")
    print(test_sql)
    print("\n匿名化后 (排除列表包含 'port', 'date', 'time'):")
    print(result1)
    print("\n映射表:")
    print(mapping1)
    
    assert 'port_number' in result1
    assert 'server_port' in result1
    assert 'create_date' in result1
    assert 'update_time' in result1
    assert 'port_config' in result1
    assert 'id' not in result1
    assert 'name' not in result1
    assert 'status' not in result1
    assert 'active' in result1
    
    print("\n✓ 测试 4 通过!")
    return True


def test_subquery():
    """测试子查询"""
    test_sql = """
SELECT *
FROM (
    SELECT user_id, user_name, create_date
    FROM users
    WHERE create_date >= '2024-01-01'
) sub
WHERE sub.user_id IN (
    SELECT user_id
    FROM orders
    WHERE status = 'active'
)
ORDER BY sub.create_date DESC
"""
    result, mapping = anonymize_sql(test_sql, exclude_list=['date', 'time'])
    
    print("\n" + "=" * 60)
    print("测试 5: 子查询")
    print("=" * 60)
    print("原始 SQL:")
    print(test_sql)
    print("\n匿名化后:")
    print(result)
    print("\n映射表:")
    print(mapping)
    
    assert 'SELECT *' in result
    assert 'sub' not in result
    assert 'IN' in result
    assert 'ORDER BY' in result
    assert 'DESC' in result
    assert 'users' not in result
    assert 'orders' not in result
    assert 'user_id' not in result
    assert 'user_name' not in result
    
    print("\n✓ 测试 5 通过!")
    return True


def test_deanonymize():
    """测试反向匿名化"""
    original_sql = """
SELECT user_id, user_name, email, create_date
FROM users
WHERE create_date >= '2024-01-01'
"""
    
    print("\n" + "=" * 60)
    print("测试 6: 反向匿名化")
    print("=" * 60)
    
    anonymized_sql, mapping = anonymize_sql(original_sql, exclude_list=['date', 'time'])
    
    print("原始 SQL:")
    print(original_sql)
    print("\n匿名化后:")
    print(anonymized_sql)
    print("\n映射表:")
    print(mapping)
    
    deanonymized_sql = deanonymize_sql(anonymized_sql, mapping)
    
    print("\n反向匿名化后:")
    print(deanonymized_sql)
    
    assert 'users' in deanonymized_sql
    assert 'user_id' in deanonymized_sql
    assert 'user_name' in deanonymized_sql
    assert 'email' in deanonymized_sql
    assert 'create_date' in deanonymized_sql
    
    print("\n✓ 测试 6 通过!")
    return True


def test_remove_comments():
    """测试删除注释和空行"""
    test_sql = """-- 这是一个行注释
SELECT user_id, user_name  -- 这是行尾注释
FROM users
/* 这是块注释 */
WHERE status = 1
-- 另一个行注释
ORDER BY user_id;
"""
    
    print("\n" + "=" * 60)
    print("测试 7: 删除注释和空行")
    print("=" * 60)
    print("原始 SQL:")
    print(test_sql)
    
    cleaned_sql = remove_comments_and_empty_lines(test_sql)
    
    print("\n清理后:")
    print(cleaned_sql)
    
    assert '-- 这是一个行注释' not in cleaned_sql
    assert '-- 这是行尾注释' not in cleaned_sql
    assert '/* 这是块注释 */' not in cleaned_sql
    assert '-- 另一个行注释' not in cleaned_sql
    
    assert 'SELECT user_id, user_name' in cleaned_sql
    assert 'FROM users' in cleaned_sql
    assert 'WHERE status = 1' in cleaned_sql
    assert 'ORDER BY user_id' in cleaned_sql
    
    print("\n✓ 测试 7 通过!")
    return True


def test_complete_flow():
    """测试完整的正向-反向匿名化流程"""
    original_sql = """
-- 查询用户信息
SELECT 
    u.user_id,
    u.user_name,
    o.order_id,
    o.order_date,
    p.product_name
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id
INNER JOIN products p ON od.product_id = p.product_id
WHERE o.order_date >= '2024-01-01'
  AND o.status = 'completed'
"""
    
    print("\n" + "=" * 60)
    print("测试 8: 完整的正向-反向匿名化流程")
    print("=" * 60)
    print("原始 SQL:")
    print(original_sql)
    
    anonymized_sql, mapping = anonymize_sql(
        original_sql, 
        exclude_list=['date', 'time'],
        remove_comments=True
    )
    
    print("\n匿名化后 (已删除注释):")
    print(anonymized_sql)
    print("\n编码字典:")
    print(mapping)
    
    deanonymized_sql = deanonymize_sql(anonymized_sql, mapping)
    
    print("\n反向匿名化后:")
    print(deanonymized_sql)
    
    assert 'users' in deanonymized_sql
    assert 'orders' in deanonymized_sql
    assert 'products' in deanonymized_sql
    assert 'user_id' in deanonymized_sql
    assert 'user_name' in deanonymized_sql
    assert 'order_id' in deanonymized_sql
    assert 'order_date' in deanonymized_sql
    assert 'product_name' in deanonymized_sql
    
    print("\n✓ 测试 8 通过!")
    return True


def run_all_tests():
    """运行所有测试"""
    print("开始运行所有测试...")
    print("=" * 60)
    
    tests = [
        ("基本 SELECT 语句", test_basic_select),
        ("带 JOIN 的复杂查询", test_complex_join),
        ("带日期格式函数的查询", test_date_format_functions),
        ("排除列表功能", test_exclude_list),
        ("子查询", test_subquery),
        ("反向匿名化", test_deanonymize),
        ("删除注释和空行", test_remove_comments),
        ("完整的正向-反向匿名化流程", test_complete_flow),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ 测试 {name} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: 通过 {passed}/{len(tests)}, 失败 {failed}/{len(tests)}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    run_all_tests()
