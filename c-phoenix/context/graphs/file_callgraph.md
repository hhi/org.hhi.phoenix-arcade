# Phoenix C-Port - File Dependency Graph

This graph simplifies the architecture by abstracting from the function-level (300+ nodes) up to the **file-level (29 nodes)**. 

- **Nodes** are the actual `.c` source files.
- **Subgraphs (Blue boxes)** are the architectural domains.
- **Arrows** indicate that *at least one function* in File A calls *at least one function* in File B.

This gives a much cleaner, 'zoomed-out' view of how data and control flows through the entire emulator, making it perfectly concise and easy to comprehend!

![File Dependency Graph](./file_callgraph.svg)
