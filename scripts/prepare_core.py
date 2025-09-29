from app.backend.data_loader import build_all_core_processed

if __name__ == "__main__":
    paths = build_all_core_processed()
    for k,v in paths.items():
        print(f"✅ Built {k}: {v}")
