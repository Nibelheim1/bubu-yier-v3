# Tiled 数据与维护说明

## 实际加载关系

`src/config/game.js` 提供关卡清单、角色和显示文案；Boot 读取 `public/assets/maps/<levelId>.json`。构建复制到 `dist/assets/maps/`。`TiledObjectFactory` 将地图对象创建为实际实体；不是根据对象名称只弹 Toast。

目前固定地图规格为 192×16，48×48 tile。`terrain` 是地形表面层：运行时读取每列第一个实心 tile，并向下形成实心地面。它不是任意悬空洞穴/多层 tile 的通用渲染器；悬空、单向平台请使用对象层。

## 支持的对象层

| 层 | 关键字段与语义 |
|---|---|
| spawn | 唯一出生点，x/y 为中心 X 与脚底 Y，facing |
| cameraBounds | 唯一相机范围，lerpX、lerpY、lookAhead |
| platforms | kind、oneWay、perfectEnabled；上表面 y，宽高为碰撞实体 |
| movingPlatforms | 上述字段 + axis、distance、speed、pingPong、startDelayMs、phase |
| temporaryPlatforms | groupId、challengeId；由开关激活碰撞 |
| perfectZones | platformId、widthRatioOverride、comboValue；平台需要 perfectEnabled |
| collectibles | value（计入本局小幸福与 Combo）、collectibleId（标识元数据） |
| springs | kind=rainbow/balloon，impulse；气球可配置 impulseX、boostMs、radius、color |
| modifiers | modifierKind=wind/conveyor/slow/slippery/bounce |
| switches | switchKind=firefly/lamp/star/spark/meteor；groupId、once、cooldownMs、activeDurationMs、challengeId |
| hazards | hazardKind、damage、response、knockbackX/Y、cooldownMs；锤子可配置 axis/distance/speed/phase |
| checkpoints | order 1/2/3、respawnX/Y、respawnFacing、heal |
| photos | photoId、challengeId，摄影点的视觉标记，不单独授予照片 |
| challengeTriggers | challengeId、challengeKind、photoId、sequence、eventCount、entryX/Y、finishX/Y、timeLimitMs、retryDelayMs、boundsLeft/Right/Bottom、failOnGround |
| storyTriggers | text、moduleIndex、once、cooldownMs，进入触发/离开恢复入口状态 |
| routeBranches | route，按每次游玩首次进入记录本地事件 |
| goal | 唯一终点；nextLevel 实际用于下一关，reunion 控制重逢演出停留时间 |

装饰性 kind、颜色、顺序标识、chapter/module 等属性可能用于绘制、数据生成或校验；不要把它们理解成任意脚本注入接口。

## 动态平台

本版统一用 `speed`（px/s），不同时保留 durationMs 的第二套时间基准。axis 只支持 horizontal/vertical；distance 使用非负长度；phase 是 0–1 的起始往返相位。`pingPong:false` 表示到达终点后停留，不瞬移回起点。

平台不可被玩家推动；侧面危险用于滑板的 sideDamage。箱体也复用这一稳定机制，不支持自由推箱和叠箱。

## Modifier

wind 使用 extraGravityY 和 airControlMultiplier，离开立即恢复。负 extraGravityY 降低净重力，不表示反重力飞行。

conveyor 使用 speed 与 direction（-1 或 1）；slow 使用 moveMultiplier；slippery 平滑水平速度；bounce 使用 impulse，内部设置重复弹起冷却。

不要在地图中保留旧 interactionKind、reachableBy、resetToCheckpoint 等未在本工程 schema 中出现的字段。旧的伤害 reset 已由 response=knockback/checkpoint 区分。两个角色都可达，因此不引入角色排他性地图条件。

## 照片步骤

`sequence` 是 JSON 字符串数组，例如：

```json
[
  {"type":"landing","id":"challenge-2-horse-0","perfect":false},
  {"type":"landing","id":"challenge-2-horse-1","perfect":false},
  {"type":"landing","id":"challenge-2-horse-2","perfect":true}
]
```

type 可来自 landing、switch、bounce 等实际事件。当前步骤满足后前进一步；到摄影终点并真正落地才成功。空中五事件挑战使用 eventCount，并对事件对象去重。

同一 challengeId 的开关、弹点和临时平台会在挑战开始/重试时一起重置。切勿把另一个摄影挑战的平台放到相同 challengeId 下。主线星桥独立于摄影组。

## 校验与修改流程

先备份 JSON，在 Tiled 中修改，然后执行 `npm run validate`。检查内容包括地图规格、唯一入口/终点/相机范围、20 小幸福的 value 合计、照片唯一性及 manifest 对应、挑战目标引用、开关组、检查点顺序、枚举、主线路径最大 gap/rise。

校验是静态一致性和基本几何筛查，不是自动寻路证明。新增复杂跳跃仍需要两角色实际运行测试。所有主线最高处必须为布布保留台阶或机关支持。

运行 `npm run build` 后用 `npm run preview` 测试构建产物，而不是只测试源码。
