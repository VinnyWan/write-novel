# 章节合约 Schema

## 文件位置

`.story-system/contracts/chapter_XXX.contract.md`

## 用途

作为大纲与正文之间的形式化桥梁。每章正文写入前必须先生成合约，正文落盘必须通过合约合规检查。

## YAML Frontmatter Schema

```yaml
# 必填字段
cbn: "本章核心：主角获得第一件法器，同时发现法器中的上古残魂"
cpns:
  - "主角进入拍卖会 → 竞拍法器 → 发现异常低价 → 成功竞得"
  - "回住处研究法器 → 滴血认主 → 残魂苏醒"
  - "残魂自我介绍 → 透露昆仑秘境线索 → 主角决定前往"
cen: "主角连夜出发前往昆仑 —— 悬念：残魂的真实身份？"
strand: quest          # quest | fire | constellation
hook_type: crisis      # crisis | suspense | desire | emotion | choice
hook_strength: strong  # strong | medium | weak
payoff_density: 3      # 本章爽点/微兑现数量（≥ 体裁画像最低要求）
target_words: 3000     # 目标字数

# 可选字段（有细纲中涉及时必填）
must_cover:
  - "法器外观与异常低价原因"
  - "滴血认主的仪式感与身体反应"
  - "残魂首次对话的语气和性格锚点"
forbidden:
  - "不要提前透露残魂的完整身份"
  - "不要在拍卖会中引入无关配角"
foreshadowing_plant:   # 本章新埋伏笔
  - "残魂提到昆仑秘境时语气的变化"
foreshadowing_recycle: # 本章需回收的伏笔
  - "第41章：拍卖行老者的异常关注"
must_advance_hooks:    # 本章必须推进的伏笔（写后自检会逐条核对是否真的推进）
  - "F003：主角对宗门的怀疑"
eligible_resolve_hooks: # 本章可回收的伏笔（不强制，写手择机填坑）
  - "F007：神秘黑令牌的来历"
characters_involved:   # 本章涉及角色
  - 主角
  - 残魂(新)
  - 拍卖师(路人)
emotion_target: "期待感 → 好奇 → 决心"  # 情绪变化轨迹
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `cbn` | string | 是 | Chapter Backbone Node，本章一句话核心 |
| `cpns` | array\[2..4\] | 是 | Core Process Nodes，2-4个子事件序列 |
| `cen` | string | 是 | Chapter End Node，章尾状态+钩子 |
| `strand` | enum | 是 | 叙事线：quest(主线) / fire(副线) / constellation(伏笔线) |
| `hook_type` | enum | 是 | 章尾钩子类型：crisis / suspense / desire / emotion / choice |
| `hook_strength` | enum | 是 | 钩子强度：strong / medium / weak |
| `payoff_density` | int | 是 | 本章微兑现数，≥ 体裁画像最低要求 |
| `target_words` | int | 是 | 目标字数 |
| `must_cover` | array | 否 | 本章必须覆盖的内容项 |
| `forbidden` | array | 否 | 本章禁止出现的内容项 |
| `foreshadowing_plant` | array | 否 | 本章新埋设的伏笔 |
| `foreshadowing_recycle` | array | 否 | 本章需回收的伏笔（含来源章） |
| `must_advance_hooks` | array | 否 | 本章必须推进的伏笔 ID 列表；写后自检逐条核对正文是否实际推进，未推进按 `hook-agenda-unfulfilled` 报错 |
| `eligible_resolve_hooks` | array | 否 | 本章可回收的伏笔 ID 列表（非强制，提示写手择机填坑） |
| `characters_involved` | array | 否 | 本章出现角色（标注"新"或"路人"） |
| `emotion_target` | string | 否 | 情绪变化轨迹 |

## 合约生命周期

```
细纲 → 合约生成 → Prewrite Gate 校验 → 正文写作 → Precommit Gate 合约合规检查 →
正文落盘 → CHAPTER_COMMIT → Postcommit Gate → 投影管线
```

## 验证规则

1. CBN 必须非空
2. CPNs 数量必须在 2-4 之间
3. CEN 必须非空且包含钩子元素
4. must_cover 每项必须在正文中可找到对应内容
5. forbidden 每项不得在正文中出现
6. payoff_density ≥ 体裁画像 density_per_chapter 最低值
7. `must_advance_hooks` 声明的每条伏笔，正文必须实际推进（写入或明显推动其状态）；未推进按 `hook-agenda-unfulfilled` 经 author_error_catalog 报为「必须处理」
8. `must_advance_hooks` 与 `eligible_resolve_hooks` 均为可选字段；缺失时跳过对应校验，不报错（向后兼容既有细纲）
