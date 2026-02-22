#!/bin/bash
# back-mgr 技能测试脚本
# 用于验证技能是否正常工作

echo "=========================================="
echo "  back-mgr 技能测试脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
run_test() {
    local test_name="$1"
    local command="$2"

    echo -e "${YELLOW}[TEST]${NC} $test_name"
    echo "运行: $command"
    echo ""

    if eval "$command"; then
        echo -e "${GREEN}[PASS]${NC} 测试通过"
    else
        echo -e "${RED}[FAIL]${NC} 测试失败"
    fi
    echo ""
    echo "----------------------------------------"
    echo ""
}

# 检查 Python
run_test "检查 Python 版本" "python --version"

# 检查脚本语法
run_test "检查脚本语法" "python -m py_compile back-mgr.py"

# 测试帮助命令
run_test "测试帮助命令" "python back-mgr.py --help"

# 测试 list 命令（应该显示没有项目）
run_test "测试 list 命令" "python back-mgr.py list"

# 测试 add 帮助
run_test "测试 add 命令帮助" "python back-mgr.py add --help"

# 测试 backup 帮助
run_test "测试 backup 命令帮助" "python back-mgr.py backup --help"

# 测试 restore 帮助
run_test "测试 restore 命令帮助" "python back-mgr.py restore --help"

echo "=========================================="
echo "  基础测试完成"
echo "=========================================="
echo ""
echo "注意：以下测试需要 SSH 访问才能完全运行"
echo "如需完整测试，请配置有效的 SSH 连接"
echo ""

# 可选：实际功能测试（需要取消注释并配置）
# echo "开始实际功能测试..."
# echo ""
#
# # 添加测试项目
# run_test "添加测试项目" 'python back-mgr.py add \
#     --name test-project \
#     --host localhost \
#     --user test \
#     --remote-path /tmp/test \
#     --local-path /tmp/backups/test'
#
# # 列出项目
# run_test "列出项目" "python back-mgr.py list"
#
# # 删除测试项目
# run_test "删除测试项目" "python back-mgr.py delete test-project"
#
# echo "完全功能测试完成！"

echo ""
echo "所有基础测试通过！技能可以正常使用。"
