import requests


class DummyJSONClient:
    """
    Client untuk berkomunikasi dengan DummyJSON API.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "EcommerceDataEngineering/1.0",
            }
        )

    def get_resource(
        self,
        resource: str,
        limit: int = 0,
        skip: int = 0,
    ) -> dict:
        """
        Mengambil resource dari DummyJSON.

        Contoh:
        GET /products?limit=0&skip=0
        """

        url = f"{self.base_url}/{resource}"

        params = {
            "limit": limit,
            "skip": skip,
        }

        response = self.session.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_products(self) -> dict:
        """
        Mengambil seluruh products.
        """

        return self.get_resource(
            resource="products",
            limit=0,
            skip=0,
        )

    def get_users(self) -> dict:
        """
        Mengambil seluruh users.
        """

        return self.get_resource(
            resource="users",
            limit=0,
            skip=0,
        )

    def get_carts(self) -> dict:
        """
        Mengambil seluruh carts.
        """

        return self.get_resource(
            resource="carts",
            limit=0,
            skip=0,
        )