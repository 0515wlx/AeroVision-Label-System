#!/usr/bin/env python3
"""
数据库迁移脚本
用于将旧版本数据库升级到新版本

变更内容：
- 添加 skipped_images 表（用于存储被跳过的废图）
"""

import sqlite3
import sys
import os

def migrate_database(db_path='./labels.db'):
    """执行数据库迁移"""

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

    print(f"📊 开始迁移数据库: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查是否已存在 skipped_images 表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='skipped_images'
        """)

        if cursor.fetchone():
            print("✅ skipped_images 表已存在，无需迁移")
            conn.close()
            return True

        print("➕ 创建 skipped_images 表...")

        # 创建跳过图片表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skipped_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                skipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()

        # 验证表是否创建成功
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='skipped_images'
        """)

        if cursor.fetchone():
            print("✅ skipped_images 表创建成功")

            # 显示所有表
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"\n📋 当前数据库包含的表: {', '.join(tables)}")

            conn.close()
            return True
        else:
            print("❌ 表创建失败")
            conn.close()
            return False

    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        return False


def check_database_version(db_path='./labels.db'):
    """检查数据库版本"""

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print(f"📋 数据库包含的表: {', '.join(tables)}")

        # 检查是否需要迁移
        if 'skipped_images' not in tables:
            print("\n⚠️  数据库需要迁移（缺少 skipped_images 表）")
            return False
        else:
            print("\n✅ 数据库是最新版本")

            # 显示统计信息
            cursor.execute('SELECT COUNT(*) FROM labels')
            labels_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM skipped_images')
            skipped_count = cursor.fetchone()[0]

            print(f"\n📊 统计信息:")
            print(f"  - 已标注: {labels_count}")
            print(f"  - 已跳过: {skipped_count}")

            return True

        conn.close()

    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("AeroVision 数据库迁移工具")
    print("=" * 60)
    print()

    # 默认数据库路径
    db_path = '../labels.db'

    # 如果提供了参数，使用参数中的路径
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    # 先检查数据库版本
    print("🔍 检查数据库版本...\n")
    needs_migration = check_database_version(db_path)

    if needs_migration is False:
        print("\n" + "=" * 60)
        print("开始迁移")
        print("=" * 60)
        print()

        # 执行迁移
        success = migrate_database(db_path)

        if success:
            print("\n" + "=" * 60)
            print("✅ 迁移完成！")
            print("=" * 60)
            print("\n可以安全地启动应用程序了。")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ 迁移失败！")
            print("=" * 60)
            print("\n请检查错误信息并重试。")
            sys.exit(1)
    elif needs_migration is True:
        print("\n数据库已是最新版本，无需迁移。")
        sys.exit(0)
    else:
        print("\n数据库检查失败，请检查数据库文件。")
        sys.exit(1)

