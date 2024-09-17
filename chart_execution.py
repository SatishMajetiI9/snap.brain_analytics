import json

def generate_chartjs_html(chart_json):
    """Generate HTML and JavaScript for rendering Chart.js chart."""
    
    chart_type = chart_json['chart_type']
    labels = chart_json['labels']
    datasets = chart_json['datasets']
    options = chart_json['options']
    
    labels_js = json.dumps(labels)
    datasets_js = json.dumps(datasets)
    
    options_js = json.dumps({
        **options,
        'responsive': True,
        'maintainAspectRatio': False,
    })
    
    chart_html = f"""
    <canvas id="myChart" style="width:500px; height:500px;"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        var ctx = document.getElementById('myChart').getContext('2d');
        var myChart = new Chart(ctx, {{
            type: '{chart_type}',  
            data: {{
                labels: {labels_js},  // Labels for the chart
                datasets: {datasets_js}  // Datasets for the chart
            }},
            options: {options_js}  // Options for the chart
        }});
    </script>
    """
    return chart_html
