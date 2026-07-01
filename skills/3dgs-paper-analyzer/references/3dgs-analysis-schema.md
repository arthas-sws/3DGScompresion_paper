# 3DGS Analysis Schema

按任务类型选择相关检查项，避免把所有论文都套成同一类。

## 通用 3DGS 检查项

- 输入：多视图图像、单图、视频、点云、深度、语义、文本或混合输入；
- 输出：新视角、几何、语义、压缩表示、SLAM 地图、可编辑资产或动态场景；
- Gaussian 参数：位置、尺度、旋转、不透明度、SH、特征、语义、时间或运动参数；
- 初始化：SfM、深度、网络预测、随机、点云或先验模型；
- 渲染：投影、tile binning、排序、alpha compositing、抗锯齿和可见性；
- 优化：损失函数、正则、学习率、训练步数、冻结策略；
- 密度控制：split、clone、prune、opacity reset、growth、merge；
- 代价：训练时间、推理 FPS、显存、模型大小、Gaussian 数量；
- 失败模式：漂浮物、几何破碎、透明/反射、运动模糊、大场景、稀疏视角。

## 压缩论文

- 压缩对象：位置、尺度、旋转、opacity、SH、feature、hash/grid、anchor 或 residual；
- 技术：剪枝、量化、熵编码、码本、稀疏化、低秩、蒸馏、神经解码器；
- 码率口径：仅 Gaussian 属性、是否包含网络权重、索引、元数据和熵模型；
- 质量指标：PSNR、SSIM、LPIPS、模型大小、解码时间、渲染 FPS；
- 可比性：同一场景、同一训练预算、同一 baseline 和同一存储统计口径；
- 风险：把解码器权重排除在模型大小之外、只报平均值、不报最差场景。

## 动态 4DGS

- 时间建模：per-frame Gaussian、deformation field、trajectory、canonical space；
- 监督：多视图视频、单目视频、光流、深度、mask、物理约束；
- 指标：动态新视角质量、时间一致性、训练/渲染速度；
- 风险：只在短序列有效、遮挡和拓扑变化失败、相机轨迹泄漏。

## SLAM / Mapping

- 传感器：RGB、RGB-D、LiDAR、IMU、event、radar；
- 地图更新：关键帧、tracking、mapping、loop closure、重定位；
- 指标：ATE、RPE、渲染质量、地图大小、实时性；
- 风险：tracking 和 rendering 指标混淆、动态物体污染地图、回环未评估。

## Feed-forward / Generalizable

- 输入视图数、相机姿态需求、尺度泛化；
- Gaussian 预测方式和 rasterizer 是否端到端；
- 与 per-scene optimization 结果的可比性；
- 训练数据覆盖范围和跨域失败。
