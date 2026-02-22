#!/usr/bin/env python3
"""
Shared utilities for LeetCode and Codeforces sync scripts
"""

import re
import json
import time
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def clean_markdown(text):
    """Remove markdown formatting like * and _ for clean output"""
    if not text:
        return text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    return text.strip()


def analyze_complexity(gemini_api_key, code, lang, max_retries=3):
    """Analyze code complexity using Gemini API with retry logic"""
    if not gemini_api_key:
        print("No Gemini API key found, skipping complexity analysis")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    headers = {'Content-Type': 'application/json'}

    prompt_text = (
        f"Analyze this {lang} code and provide ONLY the time and space complexity in Big O notation.\n\n"
        f"Code:\n{code}\n\n"
        "Respond in this EXACT JSON format with NO markdown formatting:\n"
        '{\n'
        '  "time_complexity": "O(...)",\n'
        '  "space_complexity": "O(...)",\n'
        '  "time_explanation": "brief explanation",\n'
        '  "space_explanation": "brief explanation"\n'
        '}'
    )

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500}
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                candidates = data.get('candidates', [])

                if candidates:
                    content = candidates[0]['content']['parts'][0]['text'].strip()
                    content = re.sub(r'```json\s*', '', content)
                    content = re.sub(r'```\s*', '', content)

                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1

                    if start_idx != -1 and end_idx > start_idx:
                        complexity_data = json.loads(content[start_idx:end_idx])
                        complexity_data['time_explanation'] = clean_markdown(
                            complexity_data.get('time_explanation', ''))
                        complexity_data['space_explanation'] = clean_markdown(
                            complexity_data.get('space_explanation', ''))
                        return complexity_data
                    else:
                        print(f"Could not extract JSON (attempt {attempt + 1}/{max_retries})")
                else:
                    print(f"No candidates in response (attempt {attempt + 1}/{max_retries})")
            else:
                print(f"Gemini API error: {response.status_code} (attempt {attempt + 1}/{max_retries})")

            if attempt < max_retries - 1:
                time.sleep(2 if response.status_code == 200 else 3)

        except Exception as e:
            print(f"Complexity analysis error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)

    return None


def save_performance_graph(folder_path, title, bar_labels, bar_values, bar_colors, y_label, value_fmt=None):
    """Generic helper to create and save a bar chart as performance.png"""
    try:
        fig, axes = plt.subplots(1, len(bar_labels), figsize=(6 * len(bar_labels), 5))
        if len(bar_labels) == 1:
            axes = [axes]

        for ax, label, value, color in zip(axes, bar_labels, bar_values, bar_colors):
            ax.bar([label], [value], color=color, width=0.4)
            ax.set_ylabel(y_label, fontsize=11, fontweight='bold')
            ax.set_title(label, fontsize=12, fontweight='bold')
            display = value_fmt(value) if value_fmt else str(value)
            ax.text(0, value, display, ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')

        fig.suptitle(f'Performance: {title}', fontsize=14, fontweight='bold')
        plt.tight_layout()

        graph_path = f"{folder_path}/performance.png"
        plt.savefig(graph_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Performance graph created: {graph_path}")
        return True
    except Exception as e:
        print(f"Error creating graph: {e}")
        return False


def write_complexity_section(f, complexity_data, lang_label):
    """Write complexity analysis section to a README file object"""
    f.write("## Complexity Analysis\n\n")
    f.write(f"### {lang_label}\n\n")
    f.write(f"- **Time Complexity:** {complexity_data['time_complexity']}\n")
    f.write(f"  - {complexity_data['time_explanation']}\n\n")
    f.write(f"- **Space Complexity:** {complexity_data['space_complexity']}\n")
    f.write(f"  - {complexity_data['space_explanation']}\n\n")
