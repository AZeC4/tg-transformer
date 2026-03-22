#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram .session 文件有效性检测工具
扫描 sessions 文件夹中的 .session 文件，逐个连接 Telegram 验证是否仍然有效。
"""

import asyncio
import argparse
import os
import sys
from datetime import datetime


SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")


def find_session_files(directory):
    """查找目录下所有 .session 文件"""
    if not os.path.isdir(directory):
        print(f"[错误] 目录不存在: {directory}")
        sys.exit(1)

    files = [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.endswith(".session") and os.path.isfile(os.path.join(directory, f))
    ]
    return files


async def check_one_session(session_path, proxy=None, timeout=15):
    """
    检测单个 .session 是否有效。
    返回 (文件名, 是否有效, 详情字符串)
    """
    from opentele.tl import TelegramClient
    from opentele.api import API

    name = os.path.basename(session_path)
    session_name = session_path[:-8] if session_path.endswith(".session") else session_path

    try:
        client = TelegramClient(session_name, api=API.TelegramDesktop, proxy=proxy)
        await asyncio.wait_for(client.connect(), timeout=timeout)

        if not await client.is_user_authorized():
            await client.disconnect()
            return (name, False, "未授权 / 已失效")

        me = await client.get_me()
        user_id = me.id
        phone = me.phone or "未知"
        username = f"@{me.username}" if me.username else "无用户名"
        first = me.first_name or ""
        last = me.last_name or ""
        display = f"{first} {last}".strip() or "无昵称"

        await client.disconnect()
        return (name, True, f"ID={user_id}  手机={phone}  昵称={display}  {username}")

    except asyncio.TimeoutError:
        return (name, False, "连接超时")
    except Exception as e:
        return (name, False, str(e))


async def check_all(session_files, proxy=None, concurrency=3, timeout=15):
    """并发检测所有 session 文件"""
    sem = asyncio.Semaphore(concurrency)

    async def wrapped(path):
        async with sem:
            return await check_one_session(path, proxy=proxy, timeout=timeout)

    tasks = [wrapped(f) for f in session_files]
    return await asyncio.gather(*tasks)


def parse_proxy(proxy_str):
    """解析代理字符串, 格式: ip:port"""
    if not proxy_str:
        return None
    try:
        import socks
    except ImportError:
        print("[错误] 使用代理需要 PySocks 库: pip install PySocks")
        sys.exit(1)

    parts = proxy_str.split(":")
    if len(parts) != 2:
        print("[错误] 代理格式应为 ip:port，例如 127.0.0.1:7890")
        sys.exit(1)

    ip = parts[0].strip()
    try:
        port = int(parts[1].strip())
        if not (1 <= port <= 65535):
            raise ValueError
    except ValueError:
        print("[错误] 代理端口无效，请输入 1-65535 的整数")
        sys.exit(1)

    return (socks.SOCKS5, ip, port)


def ask_proxy_interactive():
    """交互式询问用户是否启用代理及代理配置"""
    print("\n┌─────────────────────────────────┐")
    print("│      SOCKS5 代理设置            │")
    print("└─────────────────────────────────┘")
    choice = input("是否启用 SOCKS5 代理? (y/N): ").strip().lower()
    if choice not in ("y", "yes"):
        print("[信息] 不使用代理，直连 Telegram\n")
        return None

    ip = input("请输入代理 IP 地址 (默认 127.0.0.1): ").strip() or "127.0.0.1"
    port_str = input("请输入代理端口号 (默认 7890): ").strip() or "7890"

    proxy = parse_proxy(f"{ip}:{port_str}")
    print(f"[信息] 使用 SOCKS5 代理: {ip}:{port_str}\n")
    return proxy


def print_report(results):
    """打印检测报告"""
    alive = [(n, d) for n, ok, d in results if ok]
    dead = [(n, d) for n, ok, d in results if not ok]

    total = len(results)
    alive_count = len(alive)
    dead_count = len(dead)

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  Telegram Session 检测报告  —  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{sep}")
    print(f"  总计: {total}    ✅ 有效: {alive_count}    ❌ 失效: {dead_count}")
    print(sep)

    if alive:
        print("\n✅ 有效的 Session:")
        for i, (name, detail) in enumerate(alive, 1):
            print(f"  {i}. {name}")
            print(f"     {detail}")

    if dead:
        print("\n❌ 失效的 Session:")
        for i, (name, detail) in enumerate(dead, 1):
            print(f"  {i}. {name}")
            print(f"     原因: {detail}")

    print(f"\n{sep}\n")


def main():
    parser = argparse.ArgumentParser(description="检测 Telegram .session 文件是否有效")
    parser.add_argument(
        "-d", "--dir",
        default=SESSIONS_DIR,
        help=f"session 文件所在目录 (默认: {SESSIONS_DIR})",
    )
    parser.add_argument(
        "-p", "--proxy",
        default=None,
        help="SOCKS5 代理，格式: ip:port  例如 127.0.0.1:7890",
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=3,
        help="并发检测数量 (默认: 3)",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=15,
        help="单个 session 连接超时秒数 (默认: 15)",
    )
    args = parser.parse_args()

    session_files = find_session_files(args.dir)
    if not session_files:
        print(f"[提示] 在 {args.dir} 中未找到任何 .session 文件")
        sys.exit(0)

    print(f"[信息] 找到 {len(session_files)} 个 .session 文件")

    # 优先使用命令行参数，否则交互式询问
    if args.proxy:
        proxy = parse_proxy(args.proxy)
    else:
        proxy = ask_proxy_interactive()

    print("[信息] 开始检测...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(
            check_all(session_files, proxy=proxy, concurrency=args.concurrency, timeout=args.timeout)
        )
    finally:
        loop.close()

    print_report(results)


if __name__ == "__main__":
    main()
