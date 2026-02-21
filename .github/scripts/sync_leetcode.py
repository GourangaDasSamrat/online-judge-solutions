#!/usr/bin/env python3
"""
LeetCode Solutions Sync Script
Automatically syncs LeetCode submissions and generates documentation
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


class LeetCodeSync:
    def __init__(self):
        self.session = os.environ.get('LEETCODE_SESSION')
        self.csrf_token = os.environ.get('LEETCODE_CSRF')
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.base_dir = './leetcode'
        
        if not self.session or not self.csrf_token:
            raise ValueError("Missing LeetCode credentials!")
        
        os.makedirs(self.base_dir, exist_ok=True)
    
    @staticmethod
    def clean_markdown(text):
        """Remove markdown formatting like * and _ for clean output"""
        if not text:
            return text
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        return text.strip()
    
    def create_performance_graph(self, folder_path, runtime_percentile, memory_percentile, title):
        """Create a bar chart showing runtime and memory percentiles"""
        try:
            categories = ['Runtime', 'Memory']
            percentiles = [runtime_percentile, memory_percentile]
            
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(categories, percentiles, color=['#10B981', '#3B82F6'], width=0.5)
            
            ax.set_ylabel('Percentile (%)', fontsize=12, fontweight='bold')
            ax.set_title(f'Performance: {title}', fontsize=14, fontweight='bold', pad=20)
            ax.set_ylim(0, 100)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            for bar, val in zip(bars, percentiles):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.1f}%',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1, label='Median (50%)')
            ax.legend(loc='upper right')
            
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
        """Analyze code complexity using Gemini API with retry logic"""
        if not self.gemini_api_key:
            print("No Gemini API key found, skipping complexity analysis")
            return None
        
        for attempt in range(max_retries):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                
                prompt_text = "Analyze this " + lang + " code and provide ONLY the time and space complexity in Big O notation.\n\n"
                prompt_text += "Code:\n" + code + "\n\n"
                prompt_text += "Respond in this EXACT JSON format with NO markdown formatting, NO asterisks, NO underscores in explanations:\n"
                prompt_text += '{\n'
                prompt_text += '  "time_complexity": "O(...)",\n'
                prompt_text += '  "space_complexity": "O(...)",\n'
                prompt_text += '  "time_explanation": "brief explanation without any markdown formatting",\n'
                prompt_text += '  "space_explanation": "brief explanation without any markdown formatting"\n'
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
                            print(f"Could not extract JSON (attempt {attempt + 1}/{max_retries})")
                            if attempt < max_retries - 1:
                                time.sleep(2)
                                continue
                            return None
                    else:
                        print(f"No candidates in response (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        return None
                else:
                    print(f"Gemini API error: {response.status_code} (attempt {attempt + 1}/{max_retries})")
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
    
    def get_problem_details(self, title_slug):
        """Get problem details from LeetCode GraphQL API"""
        graphql_url = "https://leetcode.com/graphql"
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
        
        headers = {
            'Content-Type': 'application/json',
            'referer': 'https://leetcode.com',
        }
        
        cookies = {
            'LEETCODE_SESSION': self.session,
            'csrftoken': self.csrf_token
        }
        
        payload = {
            'query': query,
            'variables': {'titleSlug': title_slug}
        }
        
        try:
            response = requests.post(graphql_url, json=payload, headers=headers, cookies=cookies)
            data = response.json()
            if 'data' in data and data['data']['question']:
                return data['data']['question']
            return None
        except:
            return None
    
    def get_submission_details(self, submission_id):
        """Try to get detailed submission info including percentiles"""
        try:
            graphql_url = "https://leetcode.com/graphql"
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
            
            headers = {
                'Content-Type': 'application/json',
                'referer': 'https://leetcode.com',
            }
            
            cookies = {
                'LEETCODE_SESSION': self.session,
                'csrftoken': self.csrf_token
            }
            
            payload = {
                'query': query,
                'variables': {'submissionId': submission_id}
            }
            
            response = requests.post(graphql_url, json=payload, headers=headers, cookies=cookies)
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
    
    def create_problem_readme(self, folder_path, info, title_slug, performance_data, complexity_data, graph_created):
        """Create README.md for a specific problem"""
        readme_path = os.path.join(folder_path, 'README.md')
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {info['title']}\n\n")
            f.write(f"**Difficulty:** {info['difficulty']}\n\n")
            f.write(f"**Problem Link:** [LeetCode](https://leetcode.com/problems/{title_slug}/)\n\n")
            f.write(f"**Status:** Accepted\n\n")
            
            # Performance section
            if graph_created and performance_data:
                f.write("## Performance\n\n")
                f.write("![Performance Graph](./performance.png)\n\n")
            
            # Performance metrics table
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
            
            # Complexity analysis
            if complexity_data:
                f.write("## Complexity Analysis\n\n")
                for lang, complexity in complexity_data.items():
                    f.write(f"### {lang.title()}\n\n")
                    f.write(f"- **Time Complexity:** {complexity['time_complexity']}\n")
                    f.write(f"  - {complexity['time_explanation']}\n\n")
                    f.write(f"- **Space Complexity:** {complexity['space_complexity']}\n")
                    f.write(f"  - {complexity['space_explanation']}\n\n")
        
        print(f"Updated README: {readme_path}")
    
    def create_main_readme(self, processed_problems, processed_langs):
        """Create main README.md in leetcode folder"""
        print("\nCreating main README.md...")
        main_readme_path = os.path.join(self.base_dir, 'README.md')
        
        # Calculate statistics
        total_problems = len(processed_problems)
        difficulty_count = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        languages_used = set()
        
        for title_slug, info in processed_problems.items():
            difficulty = info.get('difficulty', 'Unknown')
            if difficulty in difficulty_count:
                difficulty_count[difficulty] += 1
            
            if title_slug in processed_langs:
                languages_used.update(processed_langs[title_slug])
        
        # Sort problems by number
        sorted_problems = sorted(
            processed_problems.items(),
            key=lambda x: int(x[1].get('number', '0') or '0') if x[1].get('number', '0') else 0
        )
        
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
                
                diff_emoji = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}.get(difficulty, '⚪')
                
                langs = []
                if title_slug in processed_langs:
                    langs = sorted(processed_langs[title_slug])
                
                lang_badges = " ".join([f"`{lang}`" for lang in langs])
                
                f.write(f"| {number} | [{title}](./{folder}) | {diff_emoji} {difficulty} | {lang_badges} |\n")
           
            
            f.write("## 🔗 My Profile\n\n")
            f.write("**LeetCode:** [My Profile](https://leetcode.com/u/gourangadassamrat/)\n\n")
            
            f.write("## 📈 Features\n\n")
            f.write("Each solution includes:\n")
            f.write("- ✅ Problem statement and LeetCode link\n")
            f.write("- 💻 Clean, well-commented code\n")
            f.write("- ⏱️ Time complexity analysis\n")
            f.write("- 💾 Space complexity analysis\n")
            f.write("- 📊 Performance metrics (Runtime & Memory percentiles)\n")
            f.write("- 📈 Visual performance graphs\n\n")
            
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
        
        cookies = {
            'LEETCODE_SESSION': self.session,
            'csrftoken': self.csrf_token
        }
        
        headers = {
            'referer': 'https://leetcode.com',
            'x-csrftoken': self.csrf_token
        }
        
        try:
            response = requests.get(url, cookies=cookies, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'submissions_dump' in data:
                submissions = data['submissions_dump']
                print(f"Found {len(submissions)} submissions")
                
                # Debug info
                if len(submissions) > 0:
                    print("Sample submission fields:", list(submissions[0].keys()))
                    if 'runtime_percentile' in submissions[0]:
                        print(f"Sample runtime_percentile: {submissions[0].get('runtime_percentile')}")
                    if 'memory_percentile' in submissions[0]:
                        print(f"Sample memory_percentile: {submissions[0].get('memory_percentile')}")
                
                processed_problems = {}
                processed_langs = {}
                solution_complexities = {}
                solution_performance = {}
                
                ext_map = {
                    'cpp': 'cpp', 'java': 'java', 'python': 'py',
                    'python3': 'py', 'c': 'c', 'csharp': 'cs',
                    'javascript': 'js', 'typescript': 'ts',
                    'php': 'php', 'swift': 'swift', 'kotlin': 'kt',
                    'go': 'go', 'ruby': 'rb', 'scala': 'scala',
                    'rust': 'rs'
                }
                
                for sub in submissions:
                    if sub['status_display'] == 'Accepted':
                        title_slug = sub['title_slug']
                        lang = sub['lang']
                        code = sub.get('code', '')
                        submission_id = sub.get('id')
                        
                        # Handle percentile data
                        runtime_percentile = sub.get('runtime_percentile')
                        memory_percentile = sub.get('memory_percentile')
                        
                        try:
                            runtime_percentile = float(runtime_percentile) if runtime_percentile is not None else None
                        except (ValueError, TypeError):
                            runtime_percentile = None
                        
                        try:
                            memory_percentile = float(memory_percentile) if memory_percentile is not None else None
                        except (ValueError, TypeError):
                            memory_percentile = None
                        
                        # Try GraphQL API if percentiles are None or 0
                        if (runtime_percentile is None or runtime_percentile == 0) and submission_id:
                            print(f"Trying to fetch detailed stats for submission {submission_id}...")
                            details = self.get_submission_details(submission_id)
                            if details:
                                runtime_percentile = details.get('runtime_percentile')
                                memory_percentile = details.get('memory_percentile')
                                try:
                                    runtime_percentile = float(runtime_percentile) if runtime_percentile is not None else None
                                except (ValueError, TypeError):
                                    runtime_percentile = None
                                try:
                                    memory_percentile = float(memory_percentile) if memory_percentile is not None else None
                                except (ValueError, TypeError):
                                    memory_percentile = None
                        
                        # Skip if already processed
                        if title_slug in processed_langs and lang in processed_langs[title_slug]:
                            continue
                        
                        if title_slug not in processed_langs:
                            processed_langs[title_slug] = set()
                        processed_langs[title_slug].add(lang)
                        
                        # Get problem details
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
                        
                        # Save solution
                        ext = ext_map.get(lang, 'txt')
                        filename = os.path.join(folder_name, f"solution.{ext}")
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(code)
                        
                        print(f"Saved: {filename}")
                        
                        # Store performance data
                        if runtime_percentile is not None and memory_percentile is not None:
                            if title_slug not in solution_performance:
                                solution_performance[title_slug] = {}
                            solution_performance[title_slug][lang] = {
                                'runtime_percentile': runtime_percentile,
                                'memory_percentile': memory_percentile
                            }
                            print(f"  Runtime: {runtime_percentile:.2f}%, Memory: {memory_percentile:.2f}%")
                        else:
                            print(f"  No performance data available for this submission")
                        
                        # Analyze complexity
                        if self.gemini_api_key:
                            print(f"Analyzing complexity for {title_slug} ({lang})...")
                            complexity = self.analyze_complexity(code, lang)
                            if complexity:
                                if title_slug not in solution_complexities:
                                    solution_complexities[title_slug] = {}
                                solution_complexities[title_slug][lang] = complexity
                                print(f"✓ Complexity analyzed: {complexity['time_complexity']}, {complexity['space_complexity']}")
                            time.sleep(2)
                
                # Create README files
                for title_slug, info in processed_problems.items():
                    folder_path = os.path.join(self.base_dir, info['folder'])
                    
                    # Create performance graph
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
                    
                    # Create problem README
                    self.create_problem_readme(
                        folder_path,
                        info,
                        title_slug,
                        solution_performance.get(title_slug),
                        solution_complexities.get(title_slug),
                        graph_created
                    )
                
                # Create main README
                self.create_main_readme(processed_problems, processed_langs)
                
            else:
                print("No submissions found in response")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    syncer = LeetCodeSync()
    syncer.sync()
    print("\n✅ Sync completed successfully!")
