#!/usr/bin/env python3
"""
Shared utilities for LeetCode and Codeforces sync scripts
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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

        print(f"Performance graph created: {graph_path}")
        return True
    except Exception as e:
        print(f"Error creating graph: {e}")
        return False
