import pandas as pd

from config import PROCESSED_DATA_DIR


def inspect_dataframe(
    file_name: str
) -> None:

    file_path = (
        PROCESSED_DATA_DIR /
        file_name
    )

    df = pd.read_csv(
        file_path
    )

    print()
    print("=" * 60)
    print(file_name)
    print("=" * 60)

    print("\nHEAD:")
    print(df.head())

    print("\nSHAPE:")
    print(df.shape)

    print("\nINFO:")
    print(df.info())

    print("\nCOLUMNS:")
    print(df.columns.tolist())

    print("\nNULL VALUES:")
    print(df.isnull().sum())

    print("\nDUPLICATES:")
    print(df.duplicated().sum())


def main():

    files = [
        "products_clean.csv",
        "users_clean.csv",
        "carts_clean.csv",
        "cart_items_clean.csv",
    ]

    for file_name in files:

        inspect_dataframe(
            file_name
        )


if __name__ == "__main__":
    main()