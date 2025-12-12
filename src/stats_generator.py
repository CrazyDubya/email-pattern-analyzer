"""Statistics generation and reporting module.

Generates comprehensive statistics and reports for email analysis,
including daily, weekly, monthly reports with visualizations.
"""

import logging
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

logger = logging.getLogger(__name__)


class StatsGenerator:
    """Generates statistics and reports from email analysis.
    
    Produces:
    - Daily, weekly, monthly, yearly reports
    - Visual charts and graphs
    - Exportable data in JSON, CSV, HTML formats
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the stats generator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        stats_config = self.config.get('statistics', {})
        
        self.report_types = stats_config.get('report_types', ['daily', 'weekly', 'monthly'])
        self.export_formats = stats_config.get('export_formats', ['json', 'csv'])
        self.generate_charts = stats_config.get('generate_charts', True)
        self.chart_format = stats_config.get('chart_format', 'png')
        
        # Set style for charts
        sns.set_style('whitegrid')
        
        logger.info("StatsGenerator initialized")
    
    def generate_all_reports(self, analysis_results: Dict[str, Any], 
                            output_dir: str = './data/reports') -> Dict[str, Any]:
        """Generate all configured reports.
        
        Args:
            analysis_results: Output from EmailAnalyzer
            output_dir: Directory to save reports
        
        Returns:
            Dictionary with paths to generated reports
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Generate statistics
        stats = self.generate_statistics(analysis_results)
        
        # Export in various formats
        for format_type in self.export_formats:
            if format_type == 'json':
                file_path = output_path / 'email_stats.json'
                self._export_json(stats, file_path)
                generated_files['json'] = str(file_path)
            
            elif format_type == 'csv':
                file_path = output_path / 'email_stats.csv'
                self._export_csv(stats, file_path)
                generated_files['csv'] = str(file_path)
            
            elif format_type == 'html':
                file_path = output_path / 'email_stats.html'
                self._export_html(stats, analysis_results, file_path)
                generated_files['html'] = str(file_path)
        
        # Generate charts
        if self.generate_charts:
            chart_files = self._generate_all_charts(analysis_results, output_path)
            generated_files['charts'] = chart_files
        
        logger.info(f"Generated reports in {output_dir}")
        return generated_files
    
    def generate_statistics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics."""
        stats = {
            'summary': self._generate_summary(analysis_results),
            'daily': self._generate_daily_stats(analysis_results),
            'weekly': self._generate_weekly_stats(analysis_results),
            'monthly': self._generate_monthly_stats(analysis_results),
            'sender_stats': self._generate_sender_stats(analysis_results),
            'category_stats': self._generate_category_stats(analysis_results),
            'temporal_stats': self._generate_temporal_stats(analysis_results)
        }
        
        return stats
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary statistics."""
        basic_stats = results.get('basic_stats', {})
        sender_stats = results.get('sender_stats', {})
        categories = results.get('categories', {})
        
        return {
            'total_emails': results.get('total_emails', 0),
            'date_range': basic_stats.get('date_range', {}),
            'emails_per_day': round(basic_stats.get('avg_per_day', 0), 2),
            'unique_senders': basic_stats.get('unique_senders', 0),
            'top_sender': sender_stats.get('top_sender', {}).get('email', 'N/A'),
            'dominant_category': categories.get('dominant_category', 'N/A'),
            'total_size_mb': round(basic_stats.get('total_size_mb', 0), 2)
        }
    
    def _generate_daily_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily statistics."""
        temporal = results.get('temporal_patterns', {})
        hourly_dist = temporal.get('hourly_distribution', {})
        
        # Calculate busiest hours
        if hourly_dist:
            busiest_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            quietest_hours = sorted(hourly_dist.items(), key=lambda x: x[1])[:3]
        else:
            busiest_hours = []
            quietest_hours = []
        
        return {
            'peak_hour': temporal.get('peak_hour', 'N/A'),
            'busiest_hours': [{'hour': h, 'count': c} for h, c in busiest_hours],
            'quietest_hours': [{'hour': h, 'count': c} for h, c in quietest_hours],
            'hourly_distribution': hourly_dist
        }
    
    def _generate_weekly_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly statistics."""
        temporal = results.get('temporal_patterns', {})
        daily_dist = temporal.get('daily_distribution', {})
        
        return {
            'peak_day': temporal.get('peak_day', 'N/A'),
            'daily_distribution': daily_dist,
            'weekend_percentage': round(temporal.get('weekend_percentage', 0), 2),
            'workday_pattern': 'high' if temporal.get('weekend_percentage', 0) < 20 else 'balanced'
        }
    
    def _generate_monthly_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monthly statistics."""
        temporal = results.get('temporal_patterns', {})
        monthly_trends = temporal.get('monthly_trends', {})
        
        if monthly_trends:
            avg_monthly = sum(monthly_trends.values()) / len(monthly_trends)
            peak_month = max(monthly_trends.items(), key=lambda x: x[1])
            low_month = min(monthly_trends.items(), key=lambda x: x[1])
        else:
            avg_monthly = 0
            peak_month = ('N/A', 0)
            low_month = ('N/A', 0)
        
        return {
            'monthly_trends': monthly_trends,
            'average_monthly': round(avg_monthly, 2),
            'peak_month': {'month': peak_month[0], 'count': peak_month[1]},
            'lowest_month': {'month': low_month[0], 'count': low_month[1]}
        }
    
    def _generate_sender_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sender-focused statistics."""
        sender_stats = results.get('sender_stats', {})
        
        return {
            'total_senders': sender_stats.get('total_senders', 0),
            'top_10_senders': sender_stats.get('top_senders', [])[:10],
            'sender_diversity': self._calculate_sender_diversity(sender_stats)
        }
    
    def _calculate_sender_diversity(self, sender_stats: Dict[str, Any]) -> str:
        """Calculate how diverse the sender base is."""
        top_senders = sender_stats.get('top_senders', [])
        if not top_senders:
            return 'unknown'
        
        # If top sender has more than 50%, low diversity
        if top_senders[0].get('percentage', 0) > 50:
            return 'low'
        # If top 5 have more than 80%, medium diversity
        elif sum(s.get('percentage', 0) for s in top_senders[:5]) > 80:
            return 'medium'
        else:
            return 'high'
    
    def _generate_category_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate category distribution statistics."""
        categories = results.get('categories', {}).get('distribution', {})
        
        return {
            'distribution': categories,
            'most_common': max(categories.items(), key=lambda x: x[1]['count'])[0] if categories else 'N/A',
            'category_count': len(categories)
        }
    
    def _generate_temporal_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate time-based pattern statistics."""
        patterns = results.get('patterns', {}).get('temporal', {})
        
        return {
            'time_of_day_preference': patterns.get('time_of_day', {}),
            'workweek_pattern': patterns.get('workweek_vs_weekend', {}),
            'has_routine': patterns.get('has_daily_routine', False),
            'seasonality': patterns.get('monthly_seasonality', {})
        }
    
    def _export_json(self, stats: Dict[str, Any], file_path: Path):
        """Export statistics as JSON."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        logger.info(f"Exported JSON to {file_path}")
    
    def _export_csv(self, stats: Dict[str, Any], file_path: Path):
        """Export statistics as CSV."""
        # Flatten statistics for CSV export
        rows = []
        
        # Summary stats
        summary = stats.get('summary', {})
        for key, value in summary.items():
            rows.append(['summary', key, str(value)])
        
        # Sender stats
        sender_stats = stats.get('sender_stats', {}).get('top_10_senders', [])
        for sender in sender_stats:
            rows.append(['top_sender', sender.get('email', ''), sender.get('count', 0)])
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Metric', 'Value'])
            writer.writerows(rows)
        
        logger.info(f"Exported CSV to {file_path}")
    
    def _export_html(self, stats: Dict[str, Any], results: Dict[str, Any], file_path: Path):
        """Export statistics as HTML report."""
        html_content = self._generate_html_report(stats, results)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Exported HTML to {file_path}")
    
    def _generate_html_report(self, stats: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        summary = stats.get('summary', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Email Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .stat-box {{ display: inline-block; background: #e8f5e9; padding: 20px; margin: 10px; border-radius: 5px; min-width: 200px; }}
        .stat-label {{ font-weight: bold; color: #4CAF50; }}
        .stat-value {{ font-size: 24px; color: #333; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background-color: #4CAF50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 Email Analysis Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Summary Statistics</h2>
        <div class="stat-box">
            <div class="stat-label">Total Emails</div>
            <div class="stat-value">{summary.get('total_emails', 0):,}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Emails per Day</div>
            <div class="stat-value">{summary.get('emails_per_day', 0):.1f}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Unique Senders</div>
            <div class="stat-value">{summary.get('unique_senders', 0):,}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Top Category</div>
            <div class="stat-value">{summary.get('dominant_category', 'N/A').title()}</div>
        </div>
        
        <h2>Top Senders</h2>
        <table>
            <thead>
                <tr>
                    <th>Sender</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add top senders
        for sender in stats.get('sender_stats', {}).get('top_10_senders', [])[:10]:
            html += f"""
                <tr>
                    <td>{sender.get('email', '')}</td>
                    <td>{sender.get('count', 0):,}</td>
                    <td>{sender.get('percentage', 0):.1f}%</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_all_charts(self, results: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate all visualization charts."""
        chart_files = []
        
        # Hourly distribution chart
        chart_file = self._generate_hourly_chart(results, output_dir)
        if chart_file:
            chart_files.append(chart_file)
        
        # Category distribution chart
        chart_file = self._generate_category_chart(results, output_dir)
        if chart_file:
            chart_files.append(chart_file)
        
        # Top senders chart
        chart_file = self._generate_sender_chart(results, output_dir)
        if chart_file:
            chart_files.append(chart_file)
        
        # Monthly trend chart
        chart_file = self._generate_monthly_chart(results, output_dir)
        if chart_file:
            chart_files.append(chart_file)
        
        return chart_files
    
    def _generate_hourly_chart(self, results: Dict[str, Any], output_dir: Path) -> Optional[str]:
        """Generate hourly distribution bar chart."""
        try:
            temporal = results.get('temporal_patterns', {})
            hourly_dist = temporal.get('hourly_distribution', {})
            
            if not hourly_dist:
                return None
            
            plt.figure(figsize=(12, 6))
            hours = sorted(hourly_dist.keys())
            counts = [hourly_dist[h] for h in hours]
            
            plt.bar(hours, counts, color='#4CAF50', alpha=0.7)
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Emails')
            plt.title('Email Distribution by Hour of Day')
            plt.xticks(range(0, 24))
            plt.grid(axis='y', alpha=0.3)
            
            file_path = output_dir / f'hourly_distribution.{self.chart_format}'
            plt.savefig(file_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            logger.info(f"Generated hourly chart: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error generating hourly chart: {e}")
            return None
    
    def _generate_category_chart(self, results: Dict[str, Any], output_dir: Path) -> Optional[str]:
        """Generate category distribution pie chart."""
        try:
            categories = results.get('categories', {}).get('distribution', {})
            
            if not categories:
                return None
            
            plt.figure(figsize=(10, 8))
            labels = [cat.title() for cat in categories.keys()]
            sizes = [info['count'] for info in categories.values()]
            colors = sns.color_palette('Set3', len(labels))
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Email Distribution by Category')
            plt.axis('equal')
            
            file_path = output_dir / f'category_distribution.{self.chart_format}'
            plt.savefig(file_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            logger.info(f"Generated category chart: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error generating category chart: {e}")
            return None
    
    def _generate_sender_chart(self, results: Dict[str, Any], output_dir: Path) -> Optional[str]:
        """Generate top senders horizontal bar chart."""
        try:
            sender_stats = results.get('sender_stats', {})
            top_senders = sender_stats.get('top_senders', [])[:10]
            
            if not top_senders:
                return None
            
            plt.figure(figsize=(12, 8))
            senders = [s['email'][:30] for s in top_senders]
            counts = [s['count'] for s in top_senders]
            
            plt.barh(senders, counts, color='#2196F3', alpha=0.7)
            plt.xlabel('Number of Emails')
            plt.ylabel('Sender')
            plt.title('Top 10 Email Senders')
            plt.gca().invert_yaxis()
            
            file_path = output_dir / f'top_senders.{self.chart_format}'
            plt.savefig(file_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            logger.info(f"Generated sender chart: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error generating sender chart: {e}")
            return None
    
    def _generate_monthly_chart(self, results: Dict[str, Any], output_dir: Path) -> Optional[str]:
        """Generate monthly trend line chart."""
        try:
            temporal = results.get('temporal_patterns', {})
            monthly_trends = temporal.get('monthly_trends', {})
            
            if not monthly_trends:
                return None
            
            plt.figure(figsize=(14, 6))
            months = sorted(monthly_trends.keys())
            counts = [monthly_trends[m] for m in months]
            
            plt.plot(months, counts, marker='o', linewidth=2, markersize=8, color='#FF9800')
            plt.xlabel('Month')
            plt.ylabel('Number of Emails')
            plt.title('Email Volume Trend by Month')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            
            file_path = output_dir / f'monthly_trend.{self.chart_format}'
            plt.savefig(file_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            logger.info(f"Generated monthly chart: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error generating monthly chart: {e}")
            return None
