start_research_task(
    task_violates_safety_guidelines=False,
    user_def_doesnt_want_research=False,
    response="好的，我将为您准备一份详细、中文的《Model Context Protocol（MCP）》技术白皮书，涵盖背景、发展、协议架构、技术实现、优势及应用、协议对比和未来展望等内容，并优先引用Anthropic等权威来源，应用案例将优先选取开源项目实例。预计篇幅不超过5000字，整理完毕后第一时间反馈给您。",
    title="Model Context Protocol技术白皮书",
    prompt="""
撰写一份5000字以内的《Model Context Protocol（MCP）》技术白皮书，语言为中文，内容结构如下，要求格式清晰、逻辑严谨、语言凝练并突出技术细节。优先引用Anthropic等权威来源资料，应用案例部分优先以开源项目为例。报告应包括：

一、引言
- MCP的背景与发展。
- MCP作为function call扩展的意义及目标。

二、历史背景
- 协议的起源与动机。
- MCP在大模型技术发展中的定位。

三、协议结构与工作原理
- MCP协议的完整架构及核心组件。
- 数据流在协议中的传递机制。
- MCP与function call结合的重点解析。

四、技术实现细节
- MCP的具体实现机制。
- 使用的主要技术栈与关键算法剖析。
- 数据格式、传输技术与安全保障机制。

五、优势与应用案例
- MCP对比其他协议的主要技术优势与性能表现。
- MCP在实际开源项目中的典型应用场景（如HuggingFace、Anthropic等相关开源实践案例）。

六、与其他协议的比较
- 与同类协议在功能、性能、兼容性等方面的详细对比。
- MCP的潜在改进方向。

七、总结与展望
- MCP未来发展趋势与演进路线。
- 潜在技术革新点与生态扩展前景。

请优先使用权威资料（如官方技术文档、Anthropic发表的相关论文和博客），引用内容需注明来源。制定内容提纲，按报告格式（含各级标题）输出，便于阅读和参考，语言需为中文。
"""
)