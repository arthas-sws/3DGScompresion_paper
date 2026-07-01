# 3DGS 论文专业分析框架

本文件是领域检查表。分析时按论文类型选择相关内容，不需要机械填写所有项目。

## A. 论文身份与任务范围

| 项目 | 需要确认的问题 |
|---|---|
| 论文身份 | 标题、作者、版本、年份、会议状态 |
| 任务 | 新视角合成、重建、几何、SLAM、生成、编辑、语义、压缩、仿真、机器人等 |
| 场景类型 | 静态/动态、有界/无界、物体/场景/城市尺度、室内/室外 |
| 输入 | 标定图像、单目视频、稀疏视角、RGB-D、LiDAR、文本、mesh、point cloud |
| 输出 | 可渲染场景、表面、轨迹、语义表示、重光照资产、压缩码流 |
| 关键假设 | 已知位姿、mask、深度、预训练模型、密集视角、静态光照 |
| 基线谱系 | 在什么基础方法上修改，哪些部分保持不变 |

## B. Gaussian 表示

### B.1 Primitive 类型

确认属于哪一类：

- 各向异性 3D Gaussian；
- 2D oriented Gaussian disk；
- surfel；
- anchor 与 neural offset；
- voxel/plane/Gaussian 混合；
- mesh-bound Gaussian；
- canonical dynamic Gaussian；
- 前馈网络预测的 Gaussian；
- semantic/feature Gaussian。

### B.2 参数化

根据论文记录：

- 位置或均值 \(\mu\)；
- covariance \(\Sigma\)；
- scale \(S\)；
- rotation \(R\) 或 quaternion；
- normal 或 tangent frame；
- opacity \(\alpha\)；
- color；
- SH 阶数与系数；
- appearance feature；
- semantic/language feature；
- temporal/deformation parameter；
- material/BRDF parameter；
- confidence/uncertainty；
- anchor、hierarchy、LoD、codebook 和 quantization state。

需要回答：

- 哪些参数显式存储；
- 哪些参数由 MLP 或 encoder 预测；
- 哪些参数与视角或时间有关；
- 是逐场景优化还是跨场景泛化；
- 使用了哪些约束或重参数化。

## C. 初始化与预处理

检查：

- SfM/COLMAP；
- depth 或 point cloud；
- random initialization；
- mesh initialization；
- feed-forward initialization；
- camera pose 来源与是否优化；
- mask、depth、normal、flow、semantic label；
- resize、crop、曝光处理；
- scene normalization 和坐标系；
- 初始 Gaussian 数量；
- 初始 SH degree；
- 外部预训练模型和版本。

## D. 渲染流程

按前向路径追踪：

1. 世界坐标中的 primitive；
2. 相机变换；
3. 投影到图像平面；
4. covariance/Jacobian 处理；
5. footprint、filter 和 anti-aliasing；
6. visibility、culling 和 sorting；
7. color/shading；
8. opacity 和 transmittance；
9. α 合成或其他聚合规则；
10. RGB、depth、normal、feature、semantic、uncertainty 输出。

重点判断：

- 改的是 primitive、projection、rasterizer 还是 compositing；
- 排序是精确、近似、tile-based、order-independent 还是 softmax；
- clipping 和数值稳定性如何处理；
- renderer 是 CUDA、PyTorch、Triton、OpenGL/Vulkan 还是复用实现；
- backward 是否修改；
- RGB 与 geometry buffer 是否一致。

## E. 优化与密度控制

记录：

- 优化变量；
- 冻结变量；
- optimizer；
- learning-rate group；
- schedule；
- warm-up；
- staged training；
- densification trigger；
- split/clone 规则；
- pruning 规则；
- opacity reset；
- gradient/visibility statistic；
- Gaussian budget；
- stopping criterion；
- coarse-to-fine；
- regularization。

必须分清：

- 表示创新；
- 渲染创新；
- 优化创新；
- 密度控制创新。

## F. 损失函数与监督

| 损失 | 公式/位置 | 输入 | 作用 | 权重/调度 | 代码位置 |
|---|---|---|---|---|---|

可能包括：

- L1/L2/Charbonnier；
- SSIM/D-SSIM/perceptual；
- depth/normal；
- distortion、opacity、sparsity；
- scale/covariance regularization；
- temporal consistency、flow、cycle；
- semantic contrastive/distillation；
- material/relighting；
- compression rate-distortion；
- pose/tracking；
- adversarial/diffusion guidance。

检查某个 loss 是否用于全部实验，还是只用于特定设置。

## G. 专项分支

### G.1 几何与表面重建

- surface extraction；
- SDF/TSDF/Poisson/mesh conversion；
- depth-normal consistency；
- thin structure；
- watertightness；
- geometry metrics；
- rendering–geometry trade-off。

### G.2 动态与 4D

- canonical space；
- deformation model；
- trajectory 或 latent motion；
- topology change；
- temporal regularization；
- discrete/continuous time；
- 序列长度与存储增长；
- novel-time generalization。

### G.3 语义与语言

- CLIP、DINO、SAM 或其他 feature source；
- 2D-to-3D association；
- feature dimension；
- feature compression；
- open-vocabulary protocol；
- instance consistency；
- segmentation/query metrics；
- test label 或预训练模型泄漏风险。

### G.4 压缩与传输

必须检查：

- 压缩对象：position、covariance、opacity、SH、feature、structure；
- pruning；
- quantization；
- entropy model；
- bitstream；
- codebook/vector quantization；
- rate 指标：MB、bits/Gaussian、bpp、bitrate；
- 解码时间；
- 随机访问；
- progressive transmission；
- LoD；
- 模型大小是否包含 decoder、network 和 metadata；
- 是否在 matched-rate 条件下比较质量；
- 是否提供实际码流，而非仅保存压缩 checkpoint。

### G.5 加速与部署

- training speed 与 rendering speed 分开；
- FPS 的分辨率和统计范围；
- GPU；
- precision；
- peak memory；
- custom kernel；
- mobile/embedded 假设；
- preprocessing/baking cost；
- matched-compute 下的质量损失。

### G.6 前馈与生成

- encoder/backbone；
- view/token aggregation；
- Gaussian prediction head；
- training corpus；
- generalization setting；
- inference latency；
- pose/depth dependence；
- per-scene refinement；
- generative prior。

### G.7 SLAM 与机器人

- tracking；
- mapping；
- pose optimization；
- loop closure；
- relocalization；
- dynamic object；
- online update frequency；
- ATE/RPE；
- real-time 定义；
- sensor suite；
- planning/manipulation 下游评估。

### G.8 重光照与材质

- geometry；
- albedo；
- roughness；
- metallic；
- visibility；
- illumination；
- BRDF；
- inverse-rendering ambiguity；
- relighting supervision；
- novel-light evaluation。

### G.9 大场景与城市尺度

- spatial partition；
- hierarchy/LoD；
- distributed training；
- scene stitching；
- visibility culling；
- out-of-core loading；
- seam consistency；
- storage/network cost。

## H. 实验审计

### H.1 设置表

| 数据集 | 场景/划分 | 分辨率 | 指标 | Baseline | 硬件 | 证据 |
|---|---|---|---|---|---|---|

### H.2 结果证据表

| 论文主张 | 实验证据 | 是否可比 | 提升幅度 | 是否稳定 | 限制 |
|---|---|---|---|---|---|

### H.3 消融表

| 移除/修改组件 | 预期作用 | 结果变化 | 是否支撑主张 | 混杂因素 |
|---|---|---|---|---|

检查：

- 逐场景结果；
- 是否只报平均值；
- 随机性与多次运行；
- matched Gaussian count；
- matched model size；
- matched iterations/time；
- renderer 与硬件是否一致；
- 外部监督；
- 是否缺少强 baseline；
- 是否对不同数据集单独调参；
- 定性结果是否可能挑选。

## I. 代码审计

优先检查：

- `train.py`
- `render.py`
- `eval.py`
- `scene/`
- `models/`
- `gaussian_model.py`
- `renderer/`
- `rasterizer/`
- CUDA extension
- loss 文件
- densification/pruning
- config
- dataset loader
- split 文件
- evaluation script
- environment
- submodule

对应关系分为：

- `完全对应`
- `部分对应`
- `未找到`
- `代码额外实现`
- `无法确认`

## J. 局限性与风险

分别分析：

1. 作者自述；
2. failure case；
3. 方法假设导致的局限；
4. 可复现风险；
5. 评估有效性风险；
6. 部署风险。

需要回答：

- 哪些输入条件不现实；
- 哪类场景、运动或材质会失败；
- 哪些计算成本没有计入；
- 方法如何随视角、Gaussian、帧数或 feature dimension 扩展；
- 外部预训练模型承担了多少工作；
- 对初始化、阈值和随机种子是否敏感；
- 提升是否只存在于特定数据集。
