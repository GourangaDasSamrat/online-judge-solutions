<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:8E2DE2,100:2DE2C5&height=180&section=header&text=Online%20Judge's%20Solutions&fontSize=40&fontColor=ffffff&animation=fadeIn&fontAlignY=40" width="100%"/>

<a href="https://github.com/GourangaDasSamrat/DSA/actions/workflows/leetcode-sync.yml"><img src="https://github.com/GourangaDasSamrat/DSA/actions/workflows/leetcode-sync.yml/badge.svg" alt="LeetCode Sync"/></a>
<a href="https://github.com/GourangaDasSamrat/DSA/actions/workflows/codeforces-sync.yml"><img src="https://github.com/GourangaDasSamrat/DSA/actions/workflows/codeforces-sync.yml/badge.svg" alt="Codeforces Sync"/></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/></a>

</div>

A comprehensive, self-updating archive of Data Structures and Algorithms solutions. Solutions from **LeetCode** and **Codeforces** are synced daily via GitHub Actions and get an AI-generated time/space complexity breakdown automatically. Extra practice problems and manual submissions are kept alongside in their own directories.

📂 [LeetCode](./leetcode) · [Codeforces](./codeforces) · [ic-mern-b5](./ic-mern-b5)

## Features

- **Daily sync** — accepted submissions are pulled from each platform's API automatically, no manual copy-pasting
- **AI complexity analysis** — every solution gets a time/space complexity explanation via Google Gemini
- **Performance visualizations** — runtime and memory usage are charted per problem
- **Auto-generated docs** — each problem gets its own README with the statement, approach, and analysis
- **Full history** — every attempt is version-controlled, so you can see how a solution evolved

## Structure

```text
.
├── leetcode/       # Auto-synced solutions + README + performance graphs
├── codeforces/     # Auto-synced solutions + README + performance graphs
├── ic-mern-b5/     # Manual practice solutions
└── .github/
    ├── workflows/  # Sync automation (daily 00:00 UTC)
    └── scripts/    # common.py, sync_leetcode.py, sync_codeforces.py
```

Each automated directory (`leetcode/`, `codeforces/`) has its own `README.md` with problem stats and a full solution index — start there to browse.

## How it works

Every day at 00:00 UTC, a GitHub Actions workflow fetches newly accepted submissions, analyzes their complexity with Gemini AI, generates a performance graph, writes the problem documentation, and commits the update — no manual step required.

Running it yourself needs these secrets configured in the repo:

| Secret | Used for |
|---|---|
| `LEETCODE_SESSION` | Authenticated LeetCode session cookie |
| `LEETCODE_CSRF_TOKEN` | CSRF token for LeetCode requests |
| `CODEFORCES_HANDLE` | Codeforces username to track |
| `GEMINI_API_KEY` | Complexity analysis via Google Gemini |

## Setup

```bash
git clone https://github.com/GourangaDasSamrat/DSA.git
cd DSA
pip install -r requirements.txt
```

## License

MIT — see [LICENSE](LICENSE).

---

## Author

<div align="center">

<img src="https://github.com/GourangaDasSamrat.png" width="100" height="100" style="border-radius:50%;" alt="Gouranga Das"/>

### Gouranga Das Samrat

Competitive programmer maintaining this archive as a daily practice log — solving, syncing, and documenting the process one problem at a time.

<a href="https://github.com/GourangaDasSamrat"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
<a href="https://leetcode.com/u/gourangadassamrat/"><img src="https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black"/></a>
<a href="https://codeforces.com/profile/Gouranga_Khulna"><img src="https://img.shields.io/badge/Codeforces-1F8ACB?style=for-the-badge&logo=codeforces&logoColor=white"/></a>

</div>
