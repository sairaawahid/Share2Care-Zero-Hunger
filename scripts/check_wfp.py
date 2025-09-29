from app.backend.data_loader import load_wfp_prices
if __name__ == "__main__":
    df = load_wfp_prices()
    print("Sample WFP data:")
    print(df.head())
