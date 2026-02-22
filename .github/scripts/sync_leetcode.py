#!/usr/bin/env python3
"""
LeetCode Solutions Sync Script
Automatically syncs LeetCode submissions and generates documentation
"""

import requests
import os
from datetime import datetime
import time
import traceback

from common import analyze_complexity, save_performance_graph, write_complexity_section


class LeetCodeSync:
    def __init__(self):
        self.session = os.environ.get('LEETCODE_SESSION')
        self.csrf_token = os.environ.get('LEETCODE_CSRF')
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.base_dir = './leetcode'

        if not self.session or not self.csrf_token:
            raise ValueError("Missing LeetCode credentials!")

        os.makedirs(self.base_dir, exist_ok=True)

    def _graphql_request(self, query, variables):
        """Send a request to LeetCode GraphQL API"""
        return requests.post(
            "https://leetcode.com/graphql",
            json={'query': query, 'variables': variables},
            headers={'Content-Type': 'application/json', 'referer': 'https://leetcode.com'},
            cookies={'LEETCODE_SESSION': self.session, 'csrftoken': self.csrf_token}
        )

    def create_performance_graph(self, folder_path, runtime_percentile, memory_percentile, title):
        """Create a bar chart showing runtime and memory percentiles"""
        return save_performance_graph(
            folder_path=folder_path,
            title=title,
            bar_labels=['Runtime', 'Memory'],
            bar_values=[runtime_percentile, memory_percentile],
            bar_colors=['#10B981', '#3B82F6'],
            y_label='Percentile (%)',
            value_fmt=lambda v: f'{v:.1f}%'
        )

    def analyze_complexity(self, code, lang, max_retries=3):
        """Analyze code complexity using Gemini API"""
        return analyze_complexity(self.gemini_api_key, code, lang, max_retries)

    def get_problem_details(self, title_slug):
        """Get problem details from LeetCode GraphQL API"""
        query = """
        query questionTitle($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            title
            difficulty
          }
        }
        """
        try:
            response = self._graphql_request(query, {'titleSlug': title_slug})
            data = response.json()
            if 'data' in data and data['data']['question']:
                return data['data']['question']
            return None
        except:
            return None

    def get_submission_details(self, submission_id):
        """Try to get detailed submission info including percentiles"""
        query = """
        query submissionDetails($submissionId: Int!) {
          submissionDetails(submissionId: $submissionId) {
            runtime
            runtimePercentile
            memory
            memoryPercentile
          }
        }
        """
        try:
            response = self._graphql_request(query, {'submissionId': submission_id})
            data = response.json()
            if 'data' in data and data['data'].get('submissionDetails'):
                details = data['data']['submissionDetails']
                return {
                    'runtime_percentile': details.get('runtimePercentile'),
                    'memory_percentile': details.get('memoryPercentile')
                }
            return None
        except Exception as e:
            print(f"Error fetching submission details: {e}")
            return None

    def _safe_float(self, value):
        """Safely convert a value to float, returning None on failure"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    def create_problem_readme(self, folder_path, info, title_slug, performance_data, complexity_data, graph_created):
        """Create README.md for a specific problem"""
        readme_path = os.path.join(folder_path, 'README.md')

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {info['title']}\n\n")
            f.write(f"**Difficulty:** {info['difficulty']}\n\n")
            f.write(f"**Problem Link:** [LeetCode](https://leetcode.com/problems/{title_slug}/)\n\n")
            f.write(f"**Status:** Accepted\n\n")

            if graph_created and performance_data:
                f.write("## Performance\n\n")
                f.write("![Performance Graph](./performance.png)\n\n")

            if performance_data and any(
                perf['runtime_percentile'] > 0 or perf['memory_percentile'] > 0
                for perf in performance_data.values()
            ):
                f.write("## Performance Metrics\n\n")
                f.write("| Language | Runtime Percentile | Memory Percentile |\n")
                f.write("|----------|-------------------|------------------|\n")
                for lang, perf in performance_data.items():
                    f.write(f"| {lang.title()} | {perf['runtime_percentile']:.2f}% | {perf['memory_percentile']:.2f}% |\n")
                f.write("\n")

            if complexity_data:
                f.write("## Complexity Analysis\n\n")
                for lang, complexity in complexity_data.items():
                    write_complexity_section(f, complexity, lang.title())

        print(f"Updated README: {readme_path}")

    def create_main_readme(self, processed_problems, processed_langs):
        """Create main README.md in leetcode folder"""
        print("\nCreating main README.md...")
        main_readme_path = os.path.join(self.base_dir, 'README.md')

        total_problems = len(processed_problems)
        difficulty_count = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        languages_used = set()

        for title_slug, info in processed_problems.items():
            difficulty = info.get('difficulty', 'Unknown')
            if difficulty in difficulty_count:
                difficulty_count[difficulty] += 1
            if title_slug in processed_langs:
                languages_used.update(processed_langs[title_slug])

        sorted_problems = sorted(
            processed_problems.items(),
            key=lambda x: int(x[1].get('number', '0') or '0') if x[1].get('number', '0') else 0
        )

        diff_emoji = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}

        with open(main_readme_path, 'w', encoding='utf-8') as f:
            f.write("# 🚀 LeetCode Solutions\n\n")
            f.write("My personal collection of LeetCode problem solutions, documenting my journey in mastering data structures and algorithms.\n\n")

            f.write("## 📊 Progress Statistics\n\n")
            f.write(f"**Total Problems Solved:** {total_problems}\n\n")
            f.write("| Difficulty | Count |\n")
            f.write("|------------|-------|\n")
            f.write(f"| 🟢 Easy | {difficulty_count['Easy']} |\n")
            f.write(f"| 🟡 Medium | {difficulty_count['Medium']} |\n")
            f.write(f"| 🔴 Hard | {difficulty_count['Hard']} |\n\n")

            f.write("**Languages Used:** " + ", ".join(sorted(lang.title() for lang in languages_used)) + "\n\n")

            f.write("## 📝 Problem List\n\n")
            f.write("| # | Title | Difficulty | Solution |\n")
            f.write("|---|-------|------------|----------|\n")

            for title_slug, info in sorted_problems:
                number = info.get('number', '')
                title = info.get('title', '')
                difficulty = info.get('difficulty', 'Unknown')
                folder = info.get('folder', '')
                emoji = diff_emoji.get(difficulty, '⚪')
                langs = sorted(processed_langs.get(title_slug, []))
                lang_badges = " ".join([f"`{lang}`" for lang in langs])
                f.write(f"| {number} | [{title}](./{folder}) | {emoji} {difficulty} | {lang_badges} |\n")

            f.write("## 🔗 My Profile\n\n")
            f.write("**LeetCode:** [My Profile](https://leetcode.com/u/gourangadassamrat/)\n\n")

            f.write("## 📈 Features\n\n")
            f.write("Each solution includes:\n")
            for feature in [
                "✅ Problem statement and LeetCode link",
                "💻 Clean, well-commented code",
                "⏱️ Time complexity analysis",
                "💾 Space complexity analysis",
                "📊 Performance metrics (Runtime & Memory percentiles)",
                "📈 Visual performance graphs",
            ]:
                f.write(f"- {feature}\n")
            f.write("\n")

            f.write("## 🛠️ Tech Stack\n\n")
            f.write("- **Automated Sync:** GitHub Actions\n")
            f.write("- **Complexity Analysis:** Google Gemini AI\n")
            f.write("- **Visualization:** Matplotlib\n\n")

            f.write("---\n\n")
            f.write("_🎯 Consistency is key. Keep coding, keep learning!_ 💻\n\n")
            f.write(f"_Last updated: {datetime.now().strftime('%B %d, %Y')}_\n")

        print(f"✓ Main README updated: {main_readme_path}")

    def sync(self):
        """Main sync function"""
        url = "https://leetcode.com/api/submissions/"
        cookies = {'LEETCODE_SESSION': self.session, 'csrftoken': self.csrf_token}
        headers = {'referer': 'https://leetcode.com', 'x-csrftoken': self.csrf_token}

        try:
            response = requests.get(url, cookies=cookies, headers=headers)
            response.raise_for_status()
            data = response.json()

            if 'submissions_dump' not in data:
                print("No submissions found in response")
                return

            submissions = data['submissions_dump']
            print(f"Found {len(submissions)} submissions")

            if submissions:
                print("Sample submission fields:", list(submissions[0].keys()))
                for field in ('runtime_percentile', 'memory_percentile'):
                    if field in submissions[0]:
                        print(f"Sample {field}: {submissions[0].get(field)}")

            processed_problems = {}
            processed_langs = {}
            solution_complexities = {}
            solution_performance = {}

            ext_map = {
                'cpp': 'cpp', 'java': 'java', 'python': 'py', 'python3': 'py',
                'c': 'c', 'csharp': 'cs', 'javascript': 'js', 'typescript': 'ts',
                'php': 'php', 'swift': 'swift', 'kotlin': 'kt', 'go': 'go',
                'ruby': 'rb', 'scala': 'scala', 'rust': 'rs'
            }

            for sub in submissions:
                if sub['status_display'] != 'Accepted':
                    continue

                title_slug = sub['title_slug']
                lang = sub['lang']
                code = sub.get('code', '')
                submission_id = sub.get('id')

                runtime_percentile = self._safe_float(sub.get('runtime_percentile'))
                memory_percentile = self._safe_float(sub.get('memory_percentile'))

                if (runtime_percentile is None or runtime_percentile == 0) and submission_id:
                    print(f"Trying to fetch detailed stats for submission {submission_id}...")
                    details = self.get_submission_details(submission_id)
                    if details:
                        runtime_percentile = self._safe_float(details.get('runtime_percentile'))
                        memory_percentile = self._safe_float(details.get('memory_percentile'))

                if title_slug in processed_langs and lang in processed_langs[title_slug]:
                    continue

                processed_langs.setdefault(title_slug, set()).add(lang)

                if title_slug not in processed_problems:
                    problem_info = self.get_problem_details(title_slug)
                    if problem_info:
                        processed_problems[title_slug] = {
                            'number': problem_info['questionFrontendId'],
                            'title': problem_info['title'],
                            'difficulty': problem_info['difficulty'],
                            'folder': f"{problem_info['questionFrontendId']}-{title_slug}"
                        }
                    else:
                        processed_problems[title_slug] = {
                            'number': '',
                            'title': title_slug.replace('-', ' ').title(),
                            'difficulty': 'Unknown',
                            'folder': title_slug
                        }

                folder_name = os.path.join(self.base_dir, processed_problems[title_slug]['folder'])
                os.makedirs(folder_name, exist_ok=True)

                ext = ext_map.get(lang, 'txt')
                filename = os.path.join(folder_name, f"solution.{ext}")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                print(f"Saved: {filename}")

                if runtime_percentile is not None and memory_percentile is not None:
                    solution_performance.setdefault(title_slug, {})[lang] = {
                        'runtime_percentile': runtime_percentile,
                        'memory_percentile': memory_percentile
                    }
                    print(f"  Runtime: {runtime_percentile:.2f}%, Memory: {memory_percentile:.2f}%")
                else:
                    print(f"  No performance data available for this submission")

                if self.gemini_api_key:
                    print(f"Analyzing complexity for {title_slug} ({lang})...")
                    complexity = self.analyze_complexity(code, lang)
                    if complexity:
                        solution_complexities.setdefault(title_slug, {})[lang] = complexity
                        print(f"✓ Complexity analyzed: {complexity['time_complexity']}, {complexity['space_complexity']}")
                    time.sleep(2)

            for title_slug, info in processed_problems.items():
                folder_path = os.path.join(self.base_dir, info['folder'])

                graph_created = False
                if title_slug in solution_performance:
                    first_lang = list(solution_performance[title_slug].keys())[0]
                    perf = solution_performance[title_slug][first_lang]
                    graph_created = self.create_performance_graph(
                        folder_path,
                        perf['runtime_percentile'],
                        perf['memory_percentile'],
                        info['title']
                    )

                self.create_problem_readme(
                    folder_path,
                    info,
                    title_slug,
                    solution_performance.get(title_slug),
                    solution_complexities.get(title_slug),
                    graph_created
                )

            self.create_main_readme(processed_problems, processed_langs)

        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            raise


if __name__ == "__main__":
    syncer = LeetCodeSync()
    syncer.sync()
    print("\n✅ Sync completed successfully!")
