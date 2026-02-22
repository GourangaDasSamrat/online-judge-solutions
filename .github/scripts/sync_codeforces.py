#!/usr/bin/env python3
"""
Codeforces Solutions Sync Script
Automatically syncs Codeforces submissions and generates documentation
"""

import requests
import os
from datetime import datetime
import time

from common import analyze_complexity, save_performance_graph, write_complexity_section


class CodeforcesSync:
    def __init__(self):
        self.handle = os.environ.get('CODEFORCES_HANDLE')
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.base_dir = './codeforces'

        if not self.handle:
            raise ValueError("Missing Codeforces handle!")

        os.makedirs(self.base_dir, exist_ok=True)
        self.api_base = "https://codeforces.com/api"

    def create_performance_graph(self, folder_path, time_ms, memory_kb, title):
        """Create performance visualization"""
        memory_mb = memory_kb / 1024
        return save_performance_graph(
            folder_path=folder_path,
            title=title,
            bar_labels=['Execution Time', 'Memory Usage'],
            bar_values=[time_ms, memory_mb],
            bar_colors=['#10B981', '#3B82F6'],
            y_label='Value',
            value_fmt=lambda v: f'{v} ms' if v == time_ms else f'{v:.2f} MB'
        )

    def analyze_complexity(self, code, lang, max_retries=3):
        """Analyze code complexity using Gemini API"""
        return analyze_complexity(self.gemini_api_key, code, lang, max_retries)

    def get_user_submissions(self):
        """Get all submissions from Codeforces API"""
        url = f"{self.api_base}/user.status"
        params = {'handle': self.handle, 'from': 1, 'count': 10000}

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if data['status'] == 'OK':
                return data['result']
            else:
                print(f"API Error: {data.get('comment', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"Error fetching submissions: {e}")
            return []

    def get_problem_rating(self, contest_id, index):
        """Get problem rating from Codeforces API"""
        try:
            url = f"{self.api_base}/problemset.problems"
            response = requests.get(url, timeout=30)
            data = response.json()

            if data['status'] == 'OK':
                for problem in data['result']['problems']:
                    if problem.get('contestId') == contest_id and problem.get('index') == index:
                        return problem.get('rating', 'Unrated')
            return 'Unrated'
        except:
            return 'Unrated'

    def create_problem_readme(self, folder_path, problem_info, submission_info, complexity_data, graph_created):
        """Create README.md for a specific problem"""
        readme_path = os.path.join(folder_path, 'README.md')

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {problem_info['name']}\n\n")
            f.write(f"**Contest ID:** {problem_info['contest_id']}\n\n")
            f.write(f"**Index:** {problem_info['index']}\n\n")
            f.write(f"**Rating:** {problem_info['rating']}\n\n")
            f.write(f"**Problem Link:** [Codeforces](https://codeforces.com/problemset/problem/{problem_info['contest_id']}/{problem_info['index']})\n\n")
            f.write(f"**Verdict:** {submission_info['verdict']}\n\n")

            if problem_info.get('tags'):
                f.write("**Tags:** " + ", ".join([f"`{tag}`" for tag in problem_info['tags']]) + "\n\n")

            if graph_created:
                f.write("## Performance\n\n")
                f.write("![Performance Graph](./performance.png)\n\n")

            f.write("## Performance Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Language | {submission_info['language']} |\n")
            f.write(f"| Execution Time | {submission_info['time_ms']} ms |\n")
            f.write(f"| Memory Used | {submission_info['memory_kb'] / 1024:.2f} MB |\n")
            f.write(f"| Submission Time | {submission_info['creation_time']} |\n\n")

            if complexity_data:
                write_complexity_section(f, complexity_data, submission_info['language'])

        print(f"Updated README: {readme_path}")

    def create_main_readme(self, processed_problems):
        """Create main README.md in codeforces folder"""
        print("\nCreating main README.md...")
        main_readme_path = os.path.join(self.base_dir, 'README.md')

        total_problems = len(processed_problems)
        rating_ranges = {'800-1000': 0, '1100-1300': 0, '1400-1600': 0, '1700-1900': 0, '2000+': 0, 'Unrated': 0}
        languages_used = set()
        all_tags = set()

        for info in processed_problems.values():
            rating = info.get('rating', 'Unrated')
            try:
                rating_val = int(rating)
                if rating_val <= 1000:
                    rating_ranges['800-1000'] += 1
                elif rating_val <= 1300:
                    rating_ranges['1100-1300'] += 1
                elif rating_val <= 1600:
                    rating_ranges['1400-1600'] += 1
                elif rating_val <= 1900:
                    rating_ranges['1700-1900'] += 1
                else:
                    rating_ranges['2000+'] += 1
            except:
                rating_ranges['Unrated'] += 1

            if 'language' in info:
                languages_used.add(info['language'])
            if 'tags' in info:
                all_tags.update(info['tags'])

        sorted_problems = sorted(
            processed_problems.items(),
            key=lambda x: (
                int(x[1].get('rating', '0')) if str(x[1].get('rating', '0')).isdigit() else 0,
                x[1].get('contest_id', 0),
                x[1].get('index', '')
            ),
            reverse=True
        )

        rating_emoji_map = {
            lambda v: v <= 1000: '🟢',
            lambda v: v <= 1300: '🔵',
            lambda v: v <= 1600: '🟣',
            lambda v: v <= 1900: '🟡',
        }

        def get_rating_emoji(rating):
            try:
                v = int(rating)
                if v <= 1000: return '🟢'
                if v <= 1300: return '🔵'
                if v <= 1600: return '🟣'
                if v <= 1900: return '🟡'
                return '🔴'
            except:
                return '⚪'

        with open(main_readme_path, 'w', encoding='utf-8') as f:
            f.write("# 🚀 Codeforces Solutions\n\n")
            f.write("My personal collection of Codeforces problem solutions, showcasing competitive programming skills.\n\n")

            f.write("## 📊 Progress Statistics\n\n")
            f.write(f"**Total Problems Solved:** {total_problems}\n\n")

            f.write("### By Rating\n\n")
            f.write("| Rating Range | Count |\n")
            f.write("|--------------|-------|\n")
            for rating_range, count in rating_ranges.items():
                if count > 0:
                    f.write(f"| {rating_range} | {count} |\n")
            f.write("\n")

            f.write("**Languages Used:** " + ", ".join(sorted(languages_used)) + "\n\n")

            f.write("## 📝 Problem List\n\n")
            f.write("| Contest | Index | Problem | Rating | Language |\n")
            f.write("|---------|-------|---------|--------|----------|\n")

            for _, info in sorted_problems:
                contest_id = info.get('contest_id', '')
                index = info.get('index', '')
                name = info.get('name', '')
                rating = info.get('rating', 'Unrated')
                folder = info.get('folder', '')
                language = info.get('language', '')
                emoji = get_rating_emoji(rating)
                f.write(f"| {contest_id} | {index} | [{name}](./{folder}) | {emoji} {rating} | `{language}` |\n")

            f.write("\n## 🎯 Topics Covered\n\n")
            if all_tags:
                tag_list = sorted(all_tags)
                for i in range(0, len(tag_list), 3):
                    f.write("- " + " • ".join(tag_list[i:i+3]) + "\n")
            else:
                for topic in ["Implementation", "Math", "Greedy", "Dynamic Programming", "Data Structures", "Graph Theory"]:
                    f.write(f"- {topic}\n")
            f.write("\n")

            f.write("## 🔗 My Profile\n\n")
            f.write(f"**Codeforces:** [My Profile](https://codeforces.com/profile/{self.handle})\n\n")

            f.write("## 📈 Features\n\n")
            f.write("Each solution includes:\n")
            for feature in [
                "✅ Problem statement and Codeforces link",
                "💻 Clean, optimized code",
                "⏱️ Time complexity analysis",
                "💾 Space complexity analysis",
                "📊 Performance metrics (Runtime & Memory)",
                "📈 Visual performance graphs",
                "🏷️ Problem tags and ratings",
            ]:
                f.write(f"- {feature}\n")
            f.write("\n")

            f.write("## 🛠️ Tech Stack\n\n")
            f.write("- **Automated Sync:** GitHub Actions\n")
            f.write("- **Complexity Analysis:** Google Gemini AI\n")
            f.write("- **Visualization:** Matplotlib\n")
            f.write("- **Data Source:** Codeforces API\n\n")

            f.write("---\n\n")
            f.write("_🎯 Practice makes perfect. Keep solving, keep improving!_ 💻\n\n")
            f.write(f"_Last updated: {datetime.now().strftime('%B %d, %Y')}_\n")

        print(f"✓ Main README updated: {main_readme_path}")

    def sync(self):
        """Main sync function"""
        print(f"Fetching submissions for handle: {self.handle}")
        submissions = self.get_user_submissions()

        if not submissions:
            print("No submissions found!")
            return

        print(f"Found {len(submissions)} total submissions")

        lang_ext_map = {
            'GNU C++': 'cpp', 'GNU C++11': 'cpp', 'GNU C++14': 'cpp',
            'GNU C++17': 'cpp', 'GNU C++20': 'cpp',
            'Clang++17 Diagnostics': 'cpp', 'MS C++': 'cpp',
            'Python 2': 'py', 'Python 3': 'py', 'PyPy 2': 'py', 'PyPy 3': 'py',
            'Java 8': 'java', 'Java 11': 'java',
            'Kotlin': 'kt', 'C# 8': 'cs', 'C# 10': 'cs',
            'Go': 'go', 'JavaScript': 'js', 'Rust': 'rs',
            'Ruby': 'rb', 'PHP': 'php', 'Haskell': 'hs', 'Scala': 'scala'
        }

        processed_problems = {}

        for sub in submissions:
            if sub.get('verdict') != 'OK':
                continue

            problem = sub.get('problem', {})
            contest_id = problem.get('contestId')
            index = problem.get('index')
            name = problem.get('name', 'Unknown Problem')
            tags = problem.get('tags', [])

            if not contest_id or not index:
                continue

            problem_key = f"{contest_id}_{index}"
            if problem_key in processed_problems:
                continue

            language = sub.get('programmingLanguage', 'Unknown')
            time_ms = sub.get('timeConsumedMillis', 0)
            memory_kb = sub.get('memoryConsumedBytes', 0) / 1024
            creation_time = datetime.fromtimestamp(sub.get('creationTimeSeconds', 0)).strftime('%Y-%m-%d %H:%M:%S')

            rating = self.get_problem_rating(contest_id, index)
            time.sleep(0.5)

            ext = lang_ext_map.get(language, 'txt')
            folder_name = f"{contest_id}-{index}-{name.replace(' ', '-').replace('/', '-')[:50]}"
            folder_path = os.path.join(self.base_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            code_url = f"https://codeforces.com/contest/{contest_id}/submission/{sub['id']}"
            print(f"\nProcessing: {name} ({contest_id}{index})")
            print(f"  Verdict: {sub['verdict']}, Time: {time_ms}ms, Memory: {memory_kb:.0f}KB")
            print(f"  Note: Source code must be manually added or fetched via authenticated session")

            source_file = os.path.join(folder_path, f"solution.{ext}")
            if not os.path.exists(source_file):
                with open(source_file, 'w', encoding='utf-8') as f:
                    f.write(f"// Solution for {name}\n")
                    f.write(f"// Contest: {contest_id}, Problem: {index}\n")
                    f.write(f"// Language: {language}\n")
                    f.write(f"// Verdict: {sub['verdict']}\n")
                    f.write(f"// Time: {time_ms}ms, Memory: {memory_kb:.0f}KB\n\n")
                    f.write(f"// Source code URL: {code_url}\n")
                    f.write(f"// Please add your solution code here\n")

            processed_problems[problem_key] = {
                'contest_id': contest_id,
                'index': index,
                'name': name,
                'rating': rating,
                'tags': tags,
                'folder': folder_name,
                'language': language,
                'time_ms': time_ms,
                'memory_kb': memory_kb
            }

            graph_created = self.create_performance_graph(folder_path, time_ms, memory_kb, name)

            complexity_data = None
            if os.path.exists(source_file):
                with open(source_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    if self.gemini_api_key and len(code) > 200 and "Please add your solution code here" not in code:
                        print(f"  Analyzing complexity...")
                        complexity_data = self.analyze_complexity(code, language)
                        if complexity_data:
                            print(f"  ✓ Complexity: {complexity_data['time_complexity']}, {complexity_data['space_complexity']}")
                        time.sleep(2)

            submission_info = {
                'verdict': sub['verdict'],
                'language': language,
                'time_ms': time_ms,
                'memory_kb': memory_kb,
                'creation_time': creation_time
            }

            problem_info = {
                'contest_id': contest_id,
                'index': index,
                'name': name,
                'rating': rating,
                'tags': tags
            }

            self.create_problem_readme(folder_path, problem_info, submission_info, complexity_data, graph_created)

        self.create_main_readme(processed_problems)
        print(f"\n✅ Processed {len(processed_problems)} accepted solutions")


if __name__ == "__main__":
    syncer = CodeforcesSync()
    syncer.sync()
    print("\n✅ Sync completed successfully!")
