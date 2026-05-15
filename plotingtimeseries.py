import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from TimeSeriesModelEval import load_data, build_models, train_and_predict, evaluate_models
import warnings
import json
import os


def plot_forecast(df, preds, product_name, last_n_days=28):
    """Plot actual data and baseline forecasts for a given product."""
    product_data = df.loc[df['unique_id'] == product_name].tail(last_n_days)
    product_preds = preds.loc[preds['unique_id'] == product_name]

    fig,ax = plt.subplots(figsize=(12, 5))

    ax.plot(product_data['ds'], product_data['y'],
            color='black', linewidth=2, label='Actual')

    model_config = {
        'Naive': '#e74c3c',
        'WindowAverage': '#3498db',
        'HistoricAverage': '#2ecc71',
        'SeasonalNaive': '#9b59b6',
        'AutoARIMA': '#f39c12'
    }

    # Only loop models that exist in the data
    available = [m for m in model_config if m in product_preds.columns]
    for model in available:
        ax.plot(product_preds['ds'], product_preds[model],
                color=model_config[model], linewidth=2, linestyle='--',
                marker='o', markersize=4, label=model)

    ax.axvline(x=product_data['ds'].iloc[-1], color='gray',
               linestyle=':', alpha=0.7, label='Forecast start')

    ax.set_title(f'Baseline Forecasts - {product_name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    filename = f'forecast_{product_name.lower().replace(" ", "_")}.png'
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Plot saved as: {filename}")


def save_summary(crossval_df, filename='evaluation_results.txt'):
    """Save a clean summary of model performance to a text file."""
    model_cols = ['Naive', 'WindowAverage', 'HistoricAverage', 'SeasonalNaive', 'AutoARIMA']
    model_cols = [c for c in model_cols if c in crossval_df.columns]
    baseline_cols = [c for c in model_cols if c != 'AutoARIMA']

    products = ['BAGUETTE', 'CROISSANT', 'PAIN AU CHOCOLAT',
                'TRADITIONAL BAGUETTE', 'PAIN AUX RAISINS']

    # Vectorized: calculate all errors at once
    errors = crossval_df[model_cols].subtract(crossval_df['y'], axis=0).abs()
    sq_errors = (crossval_df[model_cols].subtract(crossval_df['y'], axis=0)) ** 2

    # Overall metrics - no loops needed
    overall_mae = errors.mean().round(2)
    overall_rmse = sq_errors.mean().pow(0.5).round(2)

    # Per-product metrics - one groupby each
    product_mae = (errors.assign(uid=crossval_df['unique_id'])
                        .groupby('uid').mean().round(2))

    with open(filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("  BASELINE MODEL EVALUATION RESULTS\n")
        f.write("=" * 60 + "\n\n")

        f.write("-" * 60 + "\n")
        f.write("  OVERALL SUMMARY (average error across all products)\n")
        f.write("-" * 60 + "\n\n")

        f.write("  MAE:\n")
        for col in model_cols:
            f.write(f"    {col:20s} -->  {overall_mae[col]}\n")

        f.write("\n  RMSE:\n")
        for col in model_cols:
            f.write(f"    {col:20s} -->  {overall_rmse[col]}\n")

        winner = overall_mae.idxmin()
        f.write(f"\n  *** BEST OVERALL MODEL: {winner} (MAE = {overall_mae[winner]}) ***\n\n")

        f.write("-" * 60 + "\n")
        f.write("  PER-PRODUCT BREAKDOWN\n")
        f.write("-" * 60 + "\n\n")

        for product in products:
            if product in product_mae.index:
                f.write(f"  {product}:\n")
                for col in model_cols:
                    f.write(f"    {col:20s} -->  {product_mae.loc[product, col]}\n")
                best = product_mae.loc[product, model_cols].idxmin()
                f.write(f"    >> Best model: {best}\n\n")

        # AutoARIMA vs best baseline comparison
        f.write("-" * 60 + "\n")
        f.write("  WHAT DOES THIS MEAN?\n")
        f.write("-" * 60 + "\n\n")
        f.write("  Lower numbers = better predictions.\n")
        f.write("  MAE = average error in units (e.g. off by 5 baguettes).\n")
        f.write("  RMSE = similar but punishes big errors more.\n\n")

        if 'AutoARIMA' in model_cols and baseline_cols:
            best_baseline = overall_mae[baseline_cols].idxmin()
            best_baseline_mae = overall_mae[best_baseline]
            arima_mae = overall_mae['AutoARIMA']

            if arima_mae < best_baseline_mae:
                improvement = best_baseline_mae - arima_mae
                f.write(f"  AutoARIMA (MAE = {arima_mae}) BEAT the best baseline\n")
                f.write(f"  {best_baseline} (MAE = {best_baseline_mae}).\n")
                f.write(f"  Improvement: {improvement} units less error.\n")
                f.write("  The extra complexity is worth it!\n")
            else:
                f.write(f"  AutoARIMA (MAE = {arima_mae}) DID NOT beat the best baseline\n")
                f.write(f"  {best_baseline} (MAE = {best_baseline_mae}).\n")
                f.write("  The simpler baseline model is good enough.\n")

        f.write("=" * 60 + "\n")

    print(f"Results saved to: {filename}")


def save_and_compare(crossval_df, results_file='model_history.json'):
    """Save current results and compare with previous run - optimized."""
    model_cols = ['Naive', 'WindowAverage', 'HistoricAverage', 'SeasonalNaive', 'AutoARIMA']
    model_cols = [c for c in model_cols if c in crossval_df.columns]
    products = ['BAGUETTE', 'CROISSANT', 'PAIN AU CHOCOLAT',
                'TRADITIONAL BAGUETTE', 'PAIN AUX RAISINS']

    # Calculate ALL errors at once using vectorized pandas - no loops
    errors = crossval_df[model_cols].subtract(crossval_df['y'], axis=0).abs()

    # Overall MAE - one operation for all models
    overall_mae = errors.mean().round(2).to_dict()

    # Per-product MAE - one groupby for all models at once
    product_mae = (errors.assign(unique_id=crossval_df['unique_id'])
                        .groupby('unique_id')
                        .mean()
                        .round(2))
    product_dict = {p: product_mae.loc[p].to_dict() 
                    for p in products if p in product_mae.index}

    current = {'overall': overall_mae, 'products': product_dict}

    # Load previous results
    previous = None
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            previous = json.load(f)

    # Save current
    with open(results_file, 'w') as f:
        json.dump(current, f, indent=2)

    # Write comparison report
    with open('comparison_report.txt', 'w') as f:
        f.write("=" * 65 + "\n")
        f.write("  MODEL COMPARISON REPORT\n")
        f.write("=" * 65 + "\n\n")

        if previous is None:
            f.write("  No previous run found. This is your first run.\n")
            f.write("  Results saved. Run again after changes to see comparison.\n\n")
            f.write("-" * 65 + "\n")
            f.write("  CURRENT RESULTS (MAE)\n")
            f.write("-" * 65 + "\n\n")
            for col, val in overall_mae.items():
                f.write(f"    {col:20s} -->  {val}\n")

        else:
            # Overall comparison
            f.write("-" * 65 + "\n")
            f.write("  OVERALL COMPARISON (MAE)\n")
            f.write("-" * 65 + "\n\n")
            f.write(f"    {'Model':20s} {'Previous':>10s} {'Current':>10s} {'Change':>10s}  Result\n")
            f.write(f"    {'-'*20} {'-'*10} {'-'*10} {'-'*10}  ------\n")

            for col in model_cols:
                prev_val = previous.get('overall', {}).get(col)
                curr_val = overall_mae.get(col)
                if prev_val is not None and curr_val is not None:
                    change = curr_val - prev_val
                    result = "IMPROVED" if change < 0 else "WORSE" if change > 0 else "SAME"
                    f.write(f"    {col:20s} {prev_val:>10.2f} {curr_val:>10.2f} {change:>+10.2f}  {result}\n")

            # Per-product comparison
            f.write("\n" + "-" * 65 + "\n")
            f.write("  PER-PRODUCT COMPARISON (MAE)\n")
            f.write("-" * 65 + "\n\n")

            for product in products:
                prev_p = previous.get('products', {}).get(product, {})
                curr_p = product_dict.get(product, {})
                if curr_p:
                    f.write(f"  {product}:\n")
                    for col in model_cols:
                        prev_val = prev_p.get(col)
                        curr_val = curr_p.get(col)
                        if prev_val is not None and curr_val is not None:
                            change = curr_val - prev_val
                            arrow = "v" if change < 0 else "^" if change > 0 else "="
                            f.write(f"    {col:20s}  {prev_val:.2f} --> {curr_val:.2f}  ({change:+.2f}) {arrow}\n")
                    f.write("\n")

            # AutoARIMA summary
            f.write("-" * 65 + "\n")
            f.write("  SUMMARY\n")
            f.write("-" * 65 + "\n\n")

            prev_arima = previous.get('overall', {}).get('AutoARIMA')
            curr_arima = overall_mae.get('AutoARIMA')
            if prev_arima and curr_arima:
                change = curr_arima - prev_arima
                if change < 0:
                    f.write(f"  AutoARIMA improved by {abs(change):.2f} MAE.\n")
                    f.write("  Adding exogenous features helped!\n")
                else:
                    f.write(f"  AutoARIMA got worse by {change:.2f} MAE.\n")
                    f.write("  The extra features may be adding noise.\n")

        f.write("\n" + "=" * 65 + "\n")

    print("Comparison saved to: comparison_report.txt")

# ---- Main execution ----
if __name__ == "__main__":
    warnings.filterwarnings('ignore')

    df = load_data(os.path.join(os.path.dirname(__file__), 'french_bakery.csv'))
    models = build_models()

    focus = ['BAGUETTE', 'CROISSANT', 'PAIN AU CHOCOLAT',
             'TRADITIONAL BAGUETTE', 'PAIN AUX RAISINS']
    filtered_df = df[df['unique_id'].isin(focus)]

    # Run everything ONCE
    crossval_df = evaluate_models(filtered_df, models, product_list=focus)

    plot_forecast(filtered_df, crossval_df, 'BAGUETTE')
    plot_forecast(filtered_df, crossval_df, 'CROISSANT')

    save_summary(crossval_df, 'evaluation_results.txt')
    save_and_compare(crossval_df)

    print("\nDone! Check your folder for:")
    print("  - forecast_baguette.png")
    print("  - forecast_croissant.png")
    print("  - evaluation_results.txt")
    print("  - comparison_report.txt")