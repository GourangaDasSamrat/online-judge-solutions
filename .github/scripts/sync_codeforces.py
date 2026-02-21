#!/usr/bin/env python3
"""
Codeforces Solutions Sync Script
Automatically syncs Codeforces submissions and generates documentation
"""

import requests
import json
import os
from datetime import datetime
import time
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class CodeforcesSync:
    def __init__(self):
        self.handle = os.environ.get('CODEFORCES_HANDLE')
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.base_dir = './codeforces'
        
        if not self.handle:
            raise ValueError("Missing Codeforces handle!")
        
        os.makedirs(self.base_dir, exist_ok=True)
        self.api_base = "https://codeforces.com/api"
    
    @staticmethod
    def clean_markdown(text):
        """Remove markdown formatting"""
        if not text:
            return text
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        return text.strip()
    
    def create_performance_graph(self, folder_path, time_ms, memory_kb, title):
        """Create performance visualization"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Time graph
            ax1.bar(['Execution Time'], [time_ms], color='#10B981', width=0.4)
            ax1.set_ylabel('Time (ms)', fontsize=11, fontweight='bold')
            ax1.set_title('Runtime', fontsize=12, fontweight='bold')
            ax1.text(0, time_ms, f'{time_ms} ms', ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Memory graph
            ax2.bar(['Memory Usage'], [memory_kb / 1024], color='#3B82F6', width=0.4)
            ax2.set_ylabel('Memory (MB)', fontsize=11, fontweight='bold')
            ax2.set_title('Memory', fontsize=12, fontweight='bold')
            ax2.text(0, memory_kb / 1024, f'{memory_kb / 1024:.2f} MB', ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax2.grid(axis='y', alpha=0.3, linestyle='--')
            
            fig.suptitle(f'Performance: {title}', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            graph_path = os.path.join(folder_path, 'performance.png')
            plt.savefig(graph_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Performance graph created: {graph_path}")
            return True
        except Exception as e:
            print(f"Error creating graph: {e}")
            return False
    
    def analyze_complexity(self, code, lang, max_retries=3):
        """Analyze code complexity using Gemini API"""
        if not self.gemini_api_key:
            print("No Gemini API key found, skipping complexity analysis")
            return None
        
        for attempt in range(max_retries):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                
                prompt_text = "Analyze this " + lang + " code and provide ONLY the time and space complexity in Big O notation.\n\n"
                prompt_text += "Code:\n" + code + "\n\n"
                prompt_text += "Respond in this EXACT JSON format with NO markdown formatting:\n"
                prompt_text += '{\n'
                prompt_text += '  "time_complexity": "O(...)",\n'
                prompt_text += '  "space_complexity": "O(...)",\n'
                prompt_text += '  "time_explanation": "brief explanation",\n'
                prompt_text += '  "space_explanation": "brief explanation"\n'
                prompt_text += '}'
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt_text
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 500
                    }
                }
                
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'candidates' in data and len(data['candidates']) > 0:
                        content = data['candidates'][0]['content']['parts'][0]['text']
                        content = content.strip()
                        
                        content = re.sub(r'```json\s*', '', content)
                        content = re.sub(r'```\s*', '', content)
                        
                        start_idx = content.find('{')
                        end_idx = content.rfind('}') + 1
                        
                        if start_idx != -1 and end_idx > start_idx:
                            json_str = content[start_idx:end_idx]
                            complexity_data = json.loads(json_str)
                            
                            complexity_data['time_explanation'] = self.clean_markdown(
                                complexity_data.get('time_explanation', ''))
                            complexity_data['space_explanation'] = self.clean_markdown(
                                complexity_data.get('space_explanation', ''))
                            
                            return complexity_data
                        else:
                            if attempt < max_retries - 1:
                                time.sleep(2)
                                continue
                            return None
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        return None
                else:
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    return None
                    
            except Exception as e:
                print(f"Complexity analysis error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return None
        
        return None
    
    def get_user_submissions(self):
        """Get all submissions from Codeforces API"""
        url = f"{self.api_base}/user.status"
        params = {
            'handle': self.handle,
            'from': 1,
            'count': 10000
        }
        
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
                problems = data['result']['problems']
                for problem in problems:
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
            
            # Problem metadata
            f.write(f"**Contest ID:** {problem_info['contest_id']}\n\n")
            f.write(f"**Index:** {problem_info['index']}\n\n")
            f.write(f"**Rating:** {problem_info['rating']}\n\n")
            f.write(f"**Problem Link:** [Codeforces](https://codeforces.com/problemset/problem/{problem_info['contest_id']}/{problem_info['index']})\n\n")
            f.write(f"**Verdict:** {submission_info['verdict']}\n\n")
            
            # Tags
            if problem_info.get('tags'):
                f.write("**Tags:** " + ", ".join([f"`{tag}`" for tag in problem_info['tags']]) + "\n\n")
            
            # Performance section
            if graph_created:
                f.write("## Performance\n\n")
                f.write("![Performance Graph](./performance.png)\n\n")
            
            # Performance metrics
            f.write("## Performance Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Language | {submission_info['language']} |\n")
            f.write(f"| Execution Time | {submission_info['time_ms']} ms |\n")
            f.write(f"| Memory Used | {submission_info['memory_kb'] / 1024:.2f} MB |\n")
            f.write(f"| Submission Time | {submission_info['creation_time']} |\n\n")
            
            # Complexity analysis
            if complexity_data:
                f.write("## Complexity Analysis\n\n")
                f.write(f"### {submission_info['language']}\n\n")
                f.write(f"- **Time Complexity:** {complexity_data['time_complexity']}\n")
                f.write(f"  - {complexity_data['time_explanation']}\n\n")
                f.write(f"- **Space Complexity:** {complexity_data['space_complexity']}\n")
                f.write(f"  - {complexity_data['space_explanation']}\n\n")
        
        print(f"Updated README: {readme_path}")
    
    def create_main_readme(self, processed_problems):
        """Create main README.md in codeforces folder"""
        print("\nCreating main README.md...")
        main_readme_path = os.path.join(self.base_dir, 'README.md')
        
        # Calculate statistics
        total_problems = len(processed_problems)
        rating_ranges = {
            '800-1000': 0,
            '1100-1300': 0,
            '1400-1600': 0,
            '1700-1900': 0,
            '2000+': 0,
            'Unrated': 0
        }
        languages_used = set()
        all_tags = set()
        
        for problem_key, info in processed_problems.items():
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
        
        # Sort problems by rating
        sorted_problems = sorted(
            processed_problems.items(),
            key=lambda x: (
                int(x[1].get('rating', '0')) if str(x[1].get('rating', '0')).isdigit() else 0,
                x[1].get('contest_id', 0),
                x[1].get('index', '')
            ),
            reverse=True
        )
        
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
            
            for problem_key, info in sorted_problems:
                contest_id = info.get('contest_id', '')
                index = info.get('index', '')
                name = info.get('name', '')
                rating = info.get('rating', 'Unrated')
                folder = info.get('folder', '')
                language = info.get('language', '')
                
                # Rating color
                try:
                    rating_val = int(rating)
                    if rating_val <= 1000:
                        rating_emoji = '🟢'
                    elif rating_val <= 1300:
                        rating_emoji = '🔵'
                    elif rating_val <= 1600:
                        rating_emoji = '🟣'
                    elif rating_val <= 1900:
                        rating_emoji = '🟡'
                    else:
                        rating_emoji = '🔴'
                except:
                    rating_emoji = '⚪'
                
                f.write(f"| {contest_id} | {index} | [{name}](./{folder}) | {rating_emoji} {rating} | `{language}` |\n")
            
            f.write("\n## 🎯 Topics Covered\n\n")
            if all_tags:
                # Group tags in columns
                tag_list = sorted(all_tags)
                for i in range(0, len(tag_list), 3):
                    tags_row = tag_list[i:i+3]
                    f.write("- " + " • ".join(tags_row) + "\n")
            else:
                f.write("- Implementation\n")
                f.write("- Math\n")
                f.write("- Greedy\n")
                f.write("- Dynamic Programming\n")
                f.write("- Data Structures\n")
                f.write("- Graph Theory\n")
            f.write("\n")
            
            f.write("## 🔗 My Profile\n\n")
            f.write(f"**Codeforces:** [My Profile](https://codeforces.com/profile/{self.handle})\n\n")
            
            f.write("## 📈 Features\n\n")
            f.write("Each solution includes:\n")
            f.write("- ✅ Problem statement and Codeforces link\n")
            f.write("- 💻 Clean, optimized code\n")
            f.write("- ⏱️ Time complexity analysis\n")
            f.write("- 💾 Space complexity analysis\n")
            f.write("- 📊 Performance metrics (Runtime & Memory)\n")
            f.write("- 📈 Visual performance graphs\n")
            f.write("- 🏷️ Problem tags and ratings\n\n")
            
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
        
        # Language mapping
        lang_ext_map = {
            'GNU C++': 'cpp',
            'GNU C++11': 'cpp',
            'GNU C++14': 'cpp',
            'GNU C++17': 'cpp',
            'GNU C++20': 'cpp',
            'Clang++17 Diagnostics': 'cpp',
            'MS C++': 'cpp',
            'Python 2': 'py',
            'Python 3': 'py',
            'PyPy 2': 'py',
            'PyPy 3': 'py',
            'Java 8': 'java',
            'Java 11': 'java',
            'Kotlin': 'kt',
            'C# 8': 'cs',
            'C# 10': 'cs',
            'Go': 'go',
            'JavaScript': 'js',
            'Rust': 'rs',
            'Ruby': 'rb',
            'PHP': 'php',
            'Haskell': 'hs',
            'Scala': 'scala'
        }
        
        processed_problems = {}
        
        # Process only AC submissions
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
            
            # Skip if already processed (keep first AC)
            if problem_key in processed_problems:
                continue
            
            # Get submission details
            language = sub.get('programmingLanguage', 'Unknown')
            time_ms = sub.get('timeConsumedMillis', 0)
            memory_kb = sub.get('memoryConsumedBytes', 0) / 1024  # Convert to KB
            creation_time = datetime.fromtimestamp(sub.get('creationTimeSeconds', 0)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Get problem rating
            rating = self.get_problem_rating(contest_id, index)
            time.sleep(0.5)  # Rate limiting for API
            
            # Determine file extension
            ext = lang_ext_map.get(language, 'txt')
            
            # Create folder structure
            folder_name = f"{contest_id}-{index}-{name.replace(' ', '-').replace('/', '-')[:50]}"
            folder_path = os.path.join(self.base_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Try to fetch source code
            code_url = f"https://codeforces.com/contest/{contest_id}/submission/{sub['id']}"
            print(f"\nProcessing: {name} ({contest_id}{index})")
            print(f"  Verdict: {sub['verdict']}, Time: {time_ms}ms, Memory: {memory_kb:.0f}KB")
            print(f"  Note: Source code must be manually added or fetched via authenticated session")
            
            # Create a placeholder for source code
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
            
            # Store problem info
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
            
            # Create performance graph
            graph_created = self.create_performance_graph(
                folder_path,
                time_ms,
                memory_kb,
                name
            )
            
            # Analyze complexity (if code exists and is not placeholder)
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
            
            # Create problem README
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
            
            self.create_problem_readme(
                folder_path,
                problem_info,
                submission_info,
                complexity_data,
                graph_created
            )
        
        # Create main README
        self.create_main_readme(processed_problems)
        
        print(f"\n✅ Processed {len(processed_problems)} accepted solutions")


if __name__ == "__main__":
    syncer = CodeforcesSync()
    syncer.sync()
    print("\n✅ Sync completed successfully!")
