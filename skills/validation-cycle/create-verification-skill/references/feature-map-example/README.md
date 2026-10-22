# 特征映射示例

本目录示范 `create-verification-skill` 播种的特征映射形状：一个 README 索引加每个用户可见特征一个文件。索引逐一链接特征文件；每个特征文件回答用户视角的四个问题，并使用固定四个小节。

## 特征清单

- [示例：搜索](search.md)
- [示例：创建记录](create-record.md)

## 索引维护约定

- 每个特征文件必须由本索引链接；孤儿文件或死链都会被 `helpers/feature-map-lint.py` 报告。
- 新增用户可见特征时先加文件再加索引行，让覆盖要求先于驱动存在。
- 特征的覆盖状态（已驱动、待覆盖、verified-unreachable 及其具体前置）记录在该特征文件的 `Gotchas`。
