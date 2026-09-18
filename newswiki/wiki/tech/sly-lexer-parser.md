---
title: "SLY: lexer and parser - Playing with code"
source: "https://haqr.eu/tinycompiler/sly/"
created: "2026-07-24"
topics:
  - tech
---

# [SLY: lexer and parser - Playing with code](https://haqr.eu/tinycompiler/sly/)

SLY enables rapid development of language parsers by abstracting complex lexical and syntactic analysis into regular expressions and grammar rules.

## Key Points
- SLY is a Python library for building lexers and parsers, used to convert source code into structured syntax trees.
- Lexical analysis breaks input text into tokens (e.g., keywords, identifiers, integers) using regular expressions and finite automata.
- [[tech/sly-lexer-parser|SLY: lexer and parser]] uses rule priority to resolve ambiguities, such as distinguishing between 'int' as a type and 'inta' as an identifier.
- The parser builds a syntax tree from token streams using a context-free grammar, with support for operations like assignment, arithmetic, and expression evaluation.
- [[tech/compilers|Compiler Design]] and [[tech/ai-algorithms|AI-driven language processing]] are relevant to this work, as it demonstrates automated syntax analysis.

## Key Technical Components
- Lexical rules are defined via regular expressions (e.g., `[a-zA-Z_][a-zA-Z0-9_]*` for identifiers).
- Token priority is managed by ordering rules: `NOTEQ` before `NOT` to correctly parse `a != 0` as `ID(a) NOTEQ INTVAL(0)`.
- The parser uses a simple LALR(1) grammar to handle expressions like `x = 3+42*(s-t)` with proper operator precedence.
- Unary negation `-x` is converted to binary `0-x` to maintain consistent parsing behavior.

## Limitations and Next Steps
- The current implementation lacks semantic analysis, such as variable scoping and function overloading, which are critical for full compiler functionality.
- The compiler's output (Python code) fails to handle multiple `main` functions due to lack of scope management.
- [[tech/semantic-analysis|Semantic Analysis]] is the next logical step to improve code correctness and prevent runtime errors.
- The article demonstrates a working prototype for generating syntax trees, which can be extended to support more complex language features.

## Related Articles

- [[tech/a-road-to-lisp-why-lisp|A road to Lisp: Why Lisp]]
- [[tech/ai-food-metadata|Building Food Metadata with LLM Juries, Context Optimization & Multimodal AI]]
- [[tech/kimi-k3-pelican-benchmark|Kimi K3, and what we can still learn from the pelican benchmark]]
- [[tech/nokia-ai-datacenter-infrastructure|Nokia's New Chapter: Becoming a Supplier of AI Data Center Infrastructure]]
