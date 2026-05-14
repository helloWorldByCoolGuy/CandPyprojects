import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import Naive, HistoricAverage, WindowAverage, SeasonalNaive, AutoARIMA


def load_data(filepath):
    """Load and prepare the time series data."""
    df = pd.read_csv(filepath)
    df['ds'] = pd.to_datetime(df['ds'])
    # Keep unit_price only - no engineered features
    return df


def build_models():
    """Define baseline models."""
    models = [
        Naive(),
        WindowAverage(window_size=7),
        HistoricAverage(),
        SeasonalNaive(season_length=7),
        AutoARIMA(season_length=7, max_P=1, max_p=3, max_Q=1, max_q=3)  # new - finds best SARIMA automatically
    ]
    return models


def train_and_predict(df, models, horizon=7):
    """Fit models and return predictions."""
    sf = StatsForecast(models=models, freq="D")
    sf.fit(df=df)

    # Build future exogenous features - vectorized
    last_info = df.groupby('unique_id').agg(
        last_date=('ds', 'max'),
        unit_price=('unit_price', 'last')
    )

    # Create all future dates at once
    offsets = pd.timedelta_range(start='1D', periods=horizon, freq='D')
    future_df = (last_info.assign(key=1)
                 .merge(pd.DataFrame({'offset': offsets, 'key': 1}), on='key')
                 .drop('key', axis=1))

    future_df['ds'] = future_df['last_date'] + future_df['offset']
    future_df['day_of_week'] = future_df['ds'].dt.dayofweek
    future_df['month'] = future_df['ds'].dt.month
    future_df['is_weekend'] = (future_df['ds'].dt.dayofweek >= 5).astype(int)
    future_df = future_df.drop(['last_date', 'offset'], axis=1)
    future_df = future_df.reset_index()

    preds = sf.predict(h=horizon, X_df=future_df)
    preds = preds.reset_index()
    return preds

def evaluate_models(df, models, product_list=None, horizon=7, n_windows=2):
    """Cross-validate models and return error metrics."""
    if product_list:
        df = df[df['unique_id'].isin(product_list)]
    else:
        # Remove series that are too short
        min_length = horizon * (n_windows + 1) + 10
        series_lengths = df.groupby('unique_id').size()
        valid_ids = series_lengths[series_lengths >= min_length].index
        df = df[df['unique_id'].isin(valid_ids)]

    sf = StatsForecast(models=models, freq='D')
    crossval_df = sf.cross_validation(
        df=df,
        h=horizon,
        n_windows=n_windows
    )
    return crossval_df


# Only runs if you execute this file directly (for testing)
if __name__ == "__main__":
    df = load_data('french_bakery.csv')
    models = build_models()
    preds = train_and_predict(df, models)
    print(preds.head(14))