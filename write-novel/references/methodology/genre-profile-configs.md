# 体裁画像配置 (Genre Profile Configs)

> 13 种高频体裁的精细 YAML 配置，用于 writing agent 写作前加载体裁参数。
> 来源：基于 webnovel-writer `references/genre-profiles.md` 提取，适配纯 Markdown 流水线。

## 字段说明

| 字段 | 说明 |
|------|------|
| `id` | 唯一标识 |
| `name` | 中文名称 |
| `description` | 一句话核心卖点 |
| `hook_config.preferred_types` | 偏好钩子类型（按优先级） |
| `hook_config.strength_baseline` | 默认钩子强度：strong/medium/weak |
| `hook_config.chapter_end_required` | 章末钩子偏好 |
| `hook_config.transition_allowance` | 连续过渡章豁免上限 |
| `coolpoint_config.preferred_patterns` | 偏好爽点模式 |
| `coolpoint_config.density_per_chapter` | 每章爽点密度：high(2+)/medium(1)/low(0-1) |
| `coolpoint_config.combo_interval` | combo 爽点建议间隔（每N章） |
| `coolpoint_config.milestone_interval` | 阶段性胜利建议间隔（每N章） |
| `micropayoff_config.preferred_types` | 偏好微兑现类型 |
| `micropayoff_config.min_per_chapter` | 每章微兑现下限 |
| `micropayoff_config.transition_min` | 过渡章微兑现下限 |
| `pacing_config.stagnation_threshold` | 节奏停滞阈值（连续N章无推进=警告） |
| `pacing_config.strand_quest_max` | Quest 主线最大连续章数 |
| `pacing_config.strand_fire_gap_max` | Fire 感情线最大断档章数 |
| `pacing_config.transition_max_consecutive` | 过渡章最大连续数 |
| `override_config.allowed_rationale_types` | 允许的 Override 理由类型 |
| `override_config.debt_multiplier` | 债务倍率（>1=更严格） |
| `override_config.payback_window_default` | 默认偿还窗口（章数） |

---

## 2.1 爽文/系统流

```yaml
id: shuangwen
name: 爽文/系统流
description: 金手指开挂，快节奏升级，打脸装逼一条龙
tags: [shuangwen]

hook_config:
  preferred_types: [渴望钩, 危机钩, 情绪钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [装逼打脸, 扮猪吃虎, 越级反杀, 迪化误解]
  density_per_chapter: high
  combo_interval: 5
  milestone_interval: 10

micropayoff_config:
  preferred_types: [能力兑现, 资源兑现, 认可兑现]
  min_per_chapter: 2
  transition_min: 1

pacing_config:
  stagnation_threshold: 3
  strand_quest_max: 5
  strand_fire_gap_max: 15
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, ARC_TIMING]
  debt_multiplier: 1.0
  payback_window_default: 3
```

---

## 2.2 修仙/玄幻

```yaml
id: xianxia
name: 修仙/玄幻
description: 逆天改命，残酷法则，机缘与争斗并存
tags: [xianxia]

hook_config:
  preferred_types: [危机钩, 渴望钩, 选择钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 3

coolpoint_config:
  preferred_patterns: [越级反杀, 扮猪吃虎, 身份掉马, 反派翻车]
  density_per_chapter: high
  combo_interval: 5
  milestone_interval: 15

micropayoff_config:
  preferred_types: [能力兑现, 资源兑现, 信息兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 4
  strand_quest_max: 6
  strand_fire_gap_max: 12
  transition_max_consecutive: 3

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, WORLD_RULE_CONSTRAINT, ARC_TIMING]
  debt_multiplier: 0.9
  payback_window_default: 5
```

---

## 2.3 言情/甜宠

```yaml
id: romance
name: 言情/甜宠
description: 情感互动，关系推进，心动与虐心交织
tags: [romance]

hook_config:
  preferred_types: [情绪钩, 渴望钩, 选择钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [甜蜜超预期, 身份掉马, 迪化误解]
  density_per_chapter: medium
  combo_interval: 6
  milestone_interval: 12

micropayoff_config:
  preferred_types: [关系兑现, 情绪兑现, 认可兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 4
  strand_quest_max: 4
  strand_fire_gap_max: 5
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, CHARACTER_CREDIBILITY, ARC_TIMING]
  debt_multiplier: 1.0
  payback_window_default: 4
```

---

## 2.4 悬疑/推理

```yaml
id: mystery
name: 悬疑/推理
description: 谜题驱动，逻辑推演，真相一步步揭示
tags: [mystery]

hook_config:
  preferred_types: [悬念钩, 危机钩, 选择钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [反派翻车, 身份掉马]
  density_per_chapter: low
  combo_interval: 10
  milestone_interval: 20

micropayoff_config:
  preferred_types: [信息兑现, 线索兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 3
  strand_quest_max: 8
  strand_fire_gap_max: 20
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [LOGIC_INTEGRITY, TRANSITIONAL_SETUP, ARC_TIMING]
  debt_multiplier: 0.8
  payback_window_default: 5
```

---

## 2.5 规则怪谈

```yaml
id: rules-mystery
name: 规则怪谈
description: 诡异规则，生存推理，反杀怪谈
tags: [rules-mystery, horror]

hook_config:
  preferred_types: [危机钩, 悬念钩, 选择钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 1

coolpoint_config:
  preferred_patterns: [越级反杀, 反派翻车]
  density_per_chapter: medium
  combo_interval: 5
  milestone_interval: 8

micropayoff_config:
  preferred_types: [信息兑现, 线索兑现, 能力兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 2
  strand_quest_max: 4
  strand_fire_gap_max: 15
  transition_max_consecutive: 1

override_config:
  allowed_rationale_types: [LOGIC_INTEGRITY, WORLD_RULE_CONSTRAINT]
  debt_multiplier: 1.2
  payback_window_default: 2
```

---

## 2.6 都市异能

```yaml
id: urban-power
name: 都市异能
description: 现代背景，隐藏超能，低调装逼，产业链博弈
tags: [urban, power, industry]

hook_config:
  preferred_types: [危机钩, 渴望钩, 情绪钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [扮猪吃虎, 装逼打脸, 身份掉马, 迪化误解]
  density_per_chapter: high
  combo_interval: 3
  milestone_interval: 10

micropayoff_config:
  preferred_types: [认可兑现, 能力兑现, 关系兑现]
  min_per_chapter: 2
  transition_min: 1

pacing_config:
  stagnation_threshold: 3
  strand_quest_max: 5
  strand_fire_gap_max: 8
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, ARC_TIMING]
  debt_multiplier: 1.0
  payback_window_default: 3
```

---

## 2.7 知乎短篇

```yaml
id: zhihu-short
name: 知乎短篇
description: 短平快，强反转，情绪冲击
tags: [short, zhihu]

hook_config:
  preferred_types: [情绪钩, 悬念钩, 选择钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 0

coolpoint_config:
  preferred_patterns: [反派翻车, 身份掉马, 甜蜜超预期]
  density_per_chapter: high
  combo_interval: 2
  milestone_interval: 3

micropayoff_config:
  preferred_types: [情绪兑现, 信息兑现, 关系兑现]
  min_per_chapter: 2
  transition_min: 2

pacing_config:
  stagnation_threshold: 1
  strand_quest_max: 2
  strand_fire_gap_max: 3
  transition_max_consecutive: 0

override_config:
  allowed_rationale_types: []
  debt_multiplier: 2.0
  payback_window_default: 1
```

---

## 2.8 替身文/虐文

```yaml
id: substitute
name: 替身文/虐文
description: 情感纠葛，误解与反转，追妻火葬场
tags: [substitute, angst]

hook_config:
  preferred_types: [情绪钩, 选择钩, 悬念钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [身份掉马, 反派翻车, 甜蜜超预期]
  density_per_chapter: medium
  combo_interval: 5
  milestone_interval: 10

micropayoff_config:
  preferred_types: [情绪兑现, 关系兑现, 认可兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 3
  strand_quest_max: 3
  strand_fire_gap_max: 4
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [CHARACTER_CREDIBILITY, ARC_TIMING, TRANSITIONAL_SETUP]
  debt_multiplier: 1.0
  payback_window_default: 4
```

---

## 2.9 电竞

```yaml
id: esports
name: 电竞
description: 赛场博弈，团队磨合，逆风翻盘与冠军追逐
tags: [esports, competition]

hook_config:
  preferred_types: [危机钩, 选择钩, 渴望钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 1

coolpoint_config:
  preferred_patterns: [越级反杀, 反派翻车, 迪化误解]
  density_per_chapter: high
  combo_interval: 4
  milestone_interval: 8

micropayoff_config:
  preferred_types: [信息兑现, 认可兑现, 关系兑现]
  min_per_chapter: 2
  transition_min: 1

pacing_config:
  stagnation_threshold: 2
  strand_quest_max: 4
  strand_fire_gap_max: 8
  transition_max_consecutive: 1

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, ARC_TIMING, LOGIC_INTEGRITY]
  debt_multiplier: 1.1
  payback_window_default: 2
```

---

## 2.10 直播文

```yaml
id: livestream
name: 直播文
description: 平台流量博弈，实时反馈驱动，舆论与商业双线并进
tags: [livestream, urban]

hook_config:
  preferred_types: [危机钩, 情绪钩, 选择钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 1

coolpoint_config:
  preferred_patterns: [装逼打脸, 反派翻车, 身份掉马]
  density_per_chapter: high
  combo_interval: 3
  milestone_interval: 6

micropayoff_config:
  preferred_types: [认可兑现, 资源兑现, 信息兑现]
  min_per_chapter: 2
  transition_min: 1

pacing_config:
  stagnation_threshold: 2
  strand_quest_max: 4
  strand_fire_gap_max: 6
  transition_max_consecutive: 1

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, ARC_TIMING, CHARACTER_CREDIBILITY]
  debt_multiplier: 1.1
  payback_window_default: 2
```

---

## 2.11 克苏鲁

```yaml
id: cosmic-horror
name: 克苏鲁
description: 规则污染与理性崩塌并行，真相越近代价越高
tags: [horror, mystery, cosmic]

hook_config:
  preferred_types: [悬念钩, 危机钩, 选择钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 1

coolpoint_config:
  preferred_patterns: [反派翻车, 迪化误解, 越级反杀]
  density_per_chapter: medium
  combo_interval: 6
  milestone_interval: 10

micropayoff_config:
  preferred_types: [线索兑现, 信息兑现, 情绪兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 2
  strand_quest_max: 4
  strand_fire_gap_max: 12
  transition_max_consecutive: 1

override_config:
  allowed_rationale_types: [LOGIC_INTEGRITY, WORLD_RULE_CONSTRAINT, ARC_TIMING]
  debt_multiplier: 1.3
  payback_window_default: 2
```

---

## 2.12 历史穿越

```yaml
id: history-travel
name: 历史穿越
description: 现代灵魂穿越古代，知识优势改变历史，种田发家逆袭
tags: [history, travel, knowledge]

hook_config:
  preferred_types: [选择钩, 危机钩, 渴望钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [打脸权威, 扮猪吃虎, 反派翻车, 身份掉马]
  density_per_chapter: medium
  combo_interval: 3
  milestone_interval: 10

micropayoff_config:
  preferred_types: [信息兑现, 资源兑现, 认可兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 3
  strand_quest_max: 5
  strand_fire_gap_max: 10
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [WORLD_RULE_CONSTRAINT, CHARACTER_CREDIBILITY, ARC_TIMING]
  debt_multiplier: 0.9
  payback_window_default: 4
```

---

## 2.13 系统流

```yaml
id: system-flow
name: 系统流
description: 系统金手指驱动，任务/奖励/升级闭环，快节奏成长
tags: [system, game, shuangwen]

hook_config:
  preferred_types: [危机钩, 渴望钩, 选择钩]
  strength_baseline: strong
  chapter_end_required: true
  transition_allowance: 0

coolpoint_config:
  preferred_patterns: [越级反杀, 装逼打脸, 扮猪吃虎, 反派翻车]
  density_per_chapter: high
  combo_interval: 3
  milestone_interval: 10

micropayoff_config:
  preferred_types: [能力兑现, 资源兑现, 认可兑现]
  min_per_chapter: 2
  transition_min: 1

pacing_config:
  stagnation_threshold: 2
  strand_quest_max: 5
  strand_fire_gap_max: 15
  transition_max_consecutive: 0

override_config:
  allowed_rationale_types: [WORLD_RULE_CONSTRAINT, ARC_TIMING]
  debt_multiplier: 1.1
  payback_window_default: 2
```

---

## 默认画像（Fallback）

未配置体裁画像时使用以下默认值：

```yaml
id: default
name: 默认
description: 通用默认配置，无体裁特化参数
tags: [default]

hook_config:
  preferred_types: [危机钩, 悬念钩, 渴望钩, 情绪钩, 选择钩]
  strength_baseline: medium
  chapter_end_required: true
  transition_allowance: 2

coolpoint_config:
  preferred_patterns: [装逼打脸, 越级反杀, 身份掉马, 反派翻车]
  density_per_chapter: medium
  combo_interval: 5
  milestone_interval: 10

micropayoff_config:
  preferred_types: [能力兑现, 信息兑现, 认可兑现, 资源兑现, 关系兑现, 情绪兑现]
  min_per_chapter: 1
  transition_min: 1

pacing_config:
  stagnation_threshold: 3
  strand_quest_max: 5
  strand_fire_gap_max: 10
  transition_max_consecutive: 2

override_config:
  allowed_rationale_types: [TRANSITIONAL_SETUP, ARC_TIMING, CHARACTER_CREDIBILITY, WORLD_RULE_CONSTRAINT, LOGIC_INTEGRITY]
  debt_multiplier: 1.0
  payback_window_default: 3
```

---

## 加载指引

1. 确定项目体裁后，从上表查找对应 profile
2. 写作前将 profile 参数加载到内存：爽点密度、钩子偏好、节奏红线、微兑现下限
3. 体裁画像中找到的 profile 优先级高于默认值
4. 用户可在项目设定中覆盖任何字段

### 体裁模板 ↔ Profile 映射

| 体裁模板文件 | Profile ID |
|-------------|-----------|
| `templates/genres/修仙.md` | `xianxia` |
| `templates/genres/都市异能.md` | `urban-power` |
| `templates/genres/规则怪谈.md` | `rules-mystery` |
| `templates/genres/女频悬疑.md` | `mystery` |
| `templates/genres/知乎短篇.md` | `zhihu-short` |
| `templates/genres/替身文.md` | `substitute` |
| `templates/genres/电竞.md` | `esports` |
| `templates/genres/直播文.md` | `livestream` |
| `templates/genres/克苏鲁.md` | `cosmic-horror` |
| `templates/genres/历史古代.md` | `history-travel` |
| `templates/genres/系统流.md` | `system-flow` |
| `templates/genres/幻想言情.md` | `romance` |
| `templates/genres/都市脑洞.md` | `shuangwen` |
