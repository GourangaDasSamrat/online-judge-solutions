# Online Judge's Solutions

[![LeetCode Sync](https://github.com/GourangaDasSamrat/DSA/actions/workflows/leetcode-sync.yml/badge.svg)](https://github.com/GourangaDasSamrat/DSA/actions/workflows/leetcode-sync.yml)
[![Codeforces Sync](https://github.com/GourangaDasSamrat/DSA/actions/workflows/codeforces-sync.yml/badge.svg)](https://github.com/GourangaDasSamrat/DSA/actions/workflows/codeforces-sync.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive collection of Data Structures and Algorithms solutions from competitive programming platforms, featuring automated synchronization and AI-powered complexity analysis.

## Overview

This repository maintains an organized archive of solutions from multiple competitive programming platforms. Solutions from LeetCode and Codeforces are automatically synchronized daily via GitHub Actions, with complexity analysis powered by Google Gemini AI. Additional practice problems and manual submissions are organized in separate directories.

**Automated Platforms**: [LeetCode](./leetcode) • [Codeforces](./codeforces)

**Manual Collections**: [ic-mern-b5](./ic-mern-b5) • Other Platforms

## Features

### Automated Solutions (LeetCode, Codeforces)
- **Automated Synchronization**: Daily updates from platform APIs
- **Complexity Analysis**: AI-generated time and space complexity with explanations
- **Performance Metrics**: Runtime and memory usage tracking with visualizations
- **Comprehensive Documentation**: Auto-generated README files for each problem
- **Version Control**: Complete solution history and evolution tracking

### Manual Collections
- **Organized Structure**: Solutions grouped by topic or course
- **Learning Resources**: Additional practice problems and exercises
- **Custom Implementations**: Experimental and learning-focused code

## Repository Structure

```
.
├── leetcode/                 # LeetCode solutions (automated)
│   ├── README.md            # Statistics and problem index
│   └── [problem]/           # Individual problem directories
│       ├── README.md        # Problem details and analysis
│       ├── solution.*       # Solution implementation
│       └── performance.png  # Performance visualization
│
├── codeforces/              # Codeforces solutions (automated)
│   ├── README.md            # Statistics and problem index
│   └── [problem]/           # Individual problem directories
│       ├── README.md        # Problem details and analysis
│       ├── solution.*       # Solution implementation
│       └── performance.png  # Performance visualization
│
├── ic-mern-b5/              # Additional practice problems
│   └── [solutions]/         # Manual submissions
│
├── [other-platforms]/       # Other coding challenges
│
├── scripts/                 # Automation scripts
│   ├── common.py            # Shared utilities (complexity analysis, graph generation)
│   ├── sync_leetcode.py     # LeetCode sync script
│   └── sync_codeforces.py   # Codeforces sync script
│
└── .github/workflows/       # CI/CD configuration
    ├── leetcode-sync.yml
    └── codeforces-sync.yml
```

## Scripts

The `scripts/` directory contains three modules:

- **`common.py`** — Shared utilities used by both sync scripts: Gemini AI complexity analysis, performance graph generation, and README formatting helpers.
- **`sync_leetcode.py`** — Fetches accepted LeetCode submissions via the GraphQL API, saves solution code, and generates per-problem documentation.
- **`sync_codeforces.py`** — Fetches accepted Codeforces submissions via the Codeforces API, saves solution placeholders, and generates per-problem documentation.

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/GourangaDasSamrat/DSA.git
cd DSA

# Install dependencies (for local development)
pip install -r requirements.txt
```

### Browsing Solutions

Navigate to platform-specific directories:

```bash
# Automated platforms
cd leetcode     # LeetCode solutions (auto-synced)
cd codeforces   # Codeforces solutions (auto-synced)

# Manual collections
cd ic-mern-b5   # Additional practice problems
```

**Automated directories** contain a `README.md` with problem statistics and a complete index of solutions. Manual collections are organized by topic or course structure.

## Automation Pipeline

### Workflow

1. **Trigger**: GitHub Actions scheduled workflows (daily at 00:00 UTC)
2. **Fetch**: Retrieve accepted submissions via platform APIs
3. **Process**: Extract solution code and metadata
4. **Analyze**: Generate complexity analysis using Gemini AI (`common.py`)
5. **Visualize**: Create performance graphs with Matplotlib (`common.py`)
6. **Document**: Generate comprehensive README files
7. **Commit**: Push updates to repository

### Configuration

Automation requires the following GitHub Secrets:

**LeetCode**:
- `LEETCODE_SESSION`: Session cookie from authenticated LeetCode session
- `LEETCODE_CSRF_TOKEN`: CSRF token from LeetCode

**Codeforces**:
- `CODEFORCES_HANDLE`: Codeforces username

**Shared**:
- `GEMINI_API_KEY`: Google Gemini API key for complexity analysis

## Tech Stack

**Languages**: Python, C++, Java, JavaScript

**Automation**: GitHub Actions, Python

**APIs**: LeetCode API, Codeforces API, Google Gemini AI

**Visualization**: Matplotlib

**Version Control**: Git

## Topics Covered

**Data Structures**: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables, Heaps, Tries

**Algorithms**: Dynamic Programming, Greedy, Backtracking, Divide & Conquer, Graph Algorithms, Sorting, Searching

**Advanced Topics**: Bit Manipulation, Number Theory, Computational Geometry, String Algorithms

## Contributing

This is a personal learning repository, but suggestions and improvements are welcome.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

Please ensure:
- Code follows existing style conventions
- Documentation is updated accordingly
- All tests pass (if applicable)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Gouranga Das**

- GitHub: [@GourangaDasSamrat](https://github.com/GourangaDasSamrat)
- LeetCode: [@gourangadassamrat](https://leetcode.com/u/gourangadassamrat/)
- Codeforces: [@Gouranga_Khulna](https://codeforces.com/profile/Gouranga_Khulna)

## Acknowledgments

- LeetCode for providing the platform and API
- Codeforces for the competitive programming platform
- Google Gemini AI for complexity analysis capabilities
- GitHub Actions for automation infrastructure

---

**Note**: This repository is automatically updated. Solutions reflect personal approaches and may not represent optimal solutions for all cases.
