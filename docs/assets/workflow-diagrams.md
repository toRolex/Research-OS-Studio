# Research OS Studio - 工作流程图

## 独立入口与授权边界

README 展示可直接维护的 [workflow-v2.svg](workflow-v2.svg)。旧 PNG/JPG 保留为旧视觉资产，不再用于 README 的产品架构图。图是能力地图，不是自动状态机；已有外部 Proposal、结果或稿件都可独立进入相应路线。

```mermaid
graph TD
    U[用户显式调用：按现有材料选入口] --> A[🎯 研究方向]
    U --> V[已有 Proposal 或固定命题]
    U --> W[已有结果或稿件]
    A --> B[Idea Discovery]
    B --> C[📝 文献调研]
    C --> D[💡 候选生成]
    D --> E[🔍 查新检查]
    E --> F[👥 独立评审]
    F --> G[📋 Proposal交付]
    
    V --> HG{确认范围与本批授权：默认政策不是许可}
    HG --> H[Validation]
    G -. 用户另行调用或明确跨阶段授权 .-> HG
    H --> I[📊 实验计划]
    I --> BG{执行前核对有效本批授权与额度}
    BG --> J[⚡ 实验执行]
    J --> K[📈 结果分析]
    K --> L[🔍 独立审计]
    L --> M[📊 Claim约束]
    
    W --> WG{叶 Skill 写入与资源授权门}
    WG --> N[Writing Cycle]
    M -. 用户另行调用或明确跨阶段授权 .-> WG
    N --> O[📄 论文规划]
    O --> P[✏️ 论文起草]
    P --> Q[📊 学术图表]
    Q --> R[📖 编译检查]
    R --> S[🔍 多维度审计]
    S --> T[候选稿与审查报告；不等于科研通过]
    T -. 用户另行点名并确认具体 diff .-> R1[编译修复或引用修复]
    T -. 外发前另行批准 .-> X[投稿或上传]
    G --> STOP[报告完成不自动启动下一主流程]
    M --> STOP
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style M fill:#fff9c4
    style T fill:#f3e5f5
```

## Skills 分类结构

```mermaid
mindmap
  root((Research OS Studio))
    General
      setup-research-os
      research-os
    Idea Cycle
      idea-discovery
      research-lit
      idea-generation
      creative-thinking-for-research
      novelty-check
      idea-review
      idea-refinement
    Validation Cycle
      experiment-plan
      experiment-bridge
      run-experiment
      experiment-queue
      monitor-experiment
      training-health-check
      analyze-results
      experiment-audit
      result-to-claim
      formula-derivation
      proof-writer
      proof-review
      proof-repair
      proof-orchestrator
    Writing Cycle
      paper-writing
      ml-paper-writing
      systems-paper-writing
      paper-plan
      paper-drafting
      academic-plotting
      paper-compile
      paper-compile-repair
      citation-audit
      apply-citation-fixes
      paper-claim-audit
      claim-stress-test
      research-improvement
      rebuttal
      resubmit-pipeline
      paper-talk
```

## 用户控制关键节点

```mermaid
sequenceDiagram
    participant U as 👤 用户
    participant A as 🤖 AI Agent
    participant S as 📁 文件系统
    
    U->>A: 调用 /idea-discovery
    A->>S: 探索项目结构
    A->>U: 展示发现结果
    U->>A: 确认决策
    A->>S: 写入授权范围
    A->>U: 交付 Proposal
    Note over U,A: 用户决定下一步
```
