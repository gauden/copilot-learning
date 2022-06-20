# copilot-learning

> A personal repository for learning and exploring [Github Copilot](https://copilot.github.com).

## Rules for this exercise

1. Experiments should be short, self-contained scripts that explore the capabilities of Copilot as an extension of personal skills and knowledge in programming, especially in Python.
2. Scripts and programs should be accompanied by README files that reflect on the learning and generalizability of the work done. Use git commits to as a record of the interaction with Copilot. Assess how much of this could be done by just pressing tab after minimal inputs.
3. Experiments should take no longer than an hour each -- they are intended for someone who produces utilities that assist with other work, not to produce code as its own deliverable.
4. Ideally, but optionally, they should be finished command line applications with a defined user interface to allow reusability.
5. More rules to come as I develop an understanding of what I want to do here.

Doing it in public is scary, but hey, who's watching?

## Experiments

| Day | Note                                                              | Link                                                    |
| --- | ----------------------------------------------------------------- | ------------------------------------------------------- |
|     | **Experiment #1: Strip numbers from block of text**               |                                                         |
| 0   | _Load a text file and extract numeric information for processing_ | [number_stripper](./number_stripper/README.md)          |
|     | **Experiment #2: Query Pubmed and work with results**             |                                                         |
| 1   | Download refs by a given author from Pubmed; extract some data    | [pubmed_extract](./pubmed_extract/README.md)            |
| 2   | Refactor yesterday's code and get to core download loop           | [pubmed_extract](./pubmed_extract/README.md#version-01) |
| 3   | Divide retrieval between `esearch` and `efetch`                   | [pubmed_extract](./pubmed_extract/README.md#version-02) |
| 4   | _First fully working version, storing results of  a full search_  | [pubmed_extract](./pubmed_extract/README.md#version-03) |
| 5   | Failed attempt to automate creation of SQLite table               | [pubmed_extract](./pubmed_extract/README.md#version-04) |
| 6   | _Collect simple record for each author in the search._            | [pubmed_extract](./pubmed_extract/README.md#version-05) |
| 7   | _Parse all papers in data directory._                             | [pubmed_extract](./pubmed_extract/README.md#version-06) |
| 8   | V07.01 initial commit of SQLite feature                           | [pubmed_extract](./pubmed_extract/README.md#version-07) |
| 9   | V07.02 Minor edits to SQL feature. Some huge bug...               | [pubmed_extract](./pubmed_extract/README.md#version-08) |

_Italics_ indicate an addition to the experiment that works to spec.
