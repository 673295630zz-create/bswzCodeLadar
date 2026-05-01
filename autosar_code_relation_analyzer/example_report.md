# Code Relation Report

## Summary
- Source root: ./examples/spi_demo/src
- Number of source files: 2
- Number of functions: 1
- Number of external functions: 1
- Number of variables: 2
- Number of call relations: 1
- Number of variable relations: 4

## Function Call Relations

| Caller | Callee | Callee Type | Caller File |
|---|---|---|---|
| SpiIf_MainFunction | SpiIf_Helper | external | examples/spi_demo/src/spi_md_if.c |

## Variable Processing Relations

| Function | Variable | Relation | File | Line Hint |
|---|---|---|---|---|
| SpiIf_MainFunction | Spi_MD_If.ready_flag | writes | examples/spi_demo/src/spi_md_if.c | 14 |
| SpiIf_MainFunction | g_State | passed_by_address | examples/spi_demo/src/spi_md_if.c | 16 |
| SpiIf_MainFunction | g_State | reads | examples/spi_demo/src/spi_md_if.c | 13 |
| SpiIf_MainFunction | g_State | writes | examples/spi_demo/src/spi_md_if.c | 12 |

## Functions

### SpiIf_MainFunction
- Defined in: examples/spi_demo/src/spi_md_if.c:11-18
- Calls: SpiIf_Helper
- Reads: g_State
- Writes: Spi_MD_If.ready_flag, g_State
- Read-Writes: -
- Passed by Address: g_State

## Notes
- This is a lightweight static analyzer.
- No full macro expansion.
- No compile-time conditional branch selection.
- No real function pointer binding.
- No full type-system analysis.
- Results are for code understanding and preliminary design analysis.
