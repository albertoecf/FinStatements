import httpx


class FMPFetcher:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("FMP_API_KEY not set in environment")
        self.BASE_URL = "https://financialmodelingprep.com/api/v3"
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_income_statement(self, symbol: str, limit: int = 1):
        """
        Fetch income statement data for a given company symbol asynchronously.

        Args:
            symbol (str): Ticker symbol (e.g. AAPL, TSLA, 7203.T)
            limit (int): Number of periods to fetch (default: 1 latest)

        Returns:
            dict: Income statement data of the company

        Raises:
            httpx.HTTPStatusError: if API call fails
        """
        url = f"{self.BASE_URL}/income-statement/{symbol}"
        params = {"limit": limit, "apikey": self.api_key}

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"No income statement data found for symbol {symbol}")

        return data[0]  # Return latest income statement dict

    async def close(self):
        await self.client.aclose()
