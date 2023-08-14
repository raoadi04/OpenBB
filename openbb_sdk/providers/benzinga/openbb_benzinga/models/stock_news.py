"""Benzinga Stock News Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_news import (
    StockNewsData,
    StockNewsQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, validator

from openbb_benzinga.utils.helpers import BenzingaImage, get_data


class BenzingaStockNewsQueryParams(StockNewsQueryParams):
    """Benzinga Stock News query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html
    """

    class Config:
        fields = {"symbols": "tickers", "limit": "pageSize"}

    displayOutput: Literal["headline", "summary", "full", "all"] = Field(
        default="headline", description="The type of data to return."
    )
    date: Optional[datetime] = Field(
        default=None, description="The date of the news to retrieve."
    )
    dateFrom: Optional[datetime] = Field(
        default=None, description="The start date of the news to retrieve."
    )
    dateTo: Optional[datetime] = Field(
        default=None, description="The end date of the news to retrieve."
    )
    updatedSince: Optional[int] = Field(
        default=None,
        description="The number of seconds since the news was updated.",
    )
    publishedSince: Optional[int] = Field(
        default=None,
        description="The number of seconds since the news was published.",
    )
    sort: Optional[
        Literal[
            "published_at",
            "updated_at",
            "title",
            "author",
            "channel",
            "ticker",
            "topic",
            "content_type",
        ]
    ] = Field(
        default=None,
        description="The order in which to sort the news. Options are: published_at,"
        " updated_at, title, author, channel, ticker, topic, content_type.",
    )
    isin: Optional[str] = Field(
        default=None, description="The ISIN of the news to retrieve."
    )
    cusip: Optional[str] = Field(
        default=None, description="The CUSIP of the news to retrieve."
    )
    channels: Optional[str] = Field(
        default=None, description="The channels of the news to retrieve."
    )
    topics: Optional[str] = Field(
        default=None, description="The topics of the news to retrieve."
    )
    authors: Optional[str] = Field(
        default=None, description="The authors of the news to retrieve."
    )
    content_types: Optional[str] = Field(
        default=None, description="The content types of the news to retrieve."
    )


class BenzingaStockNewsData(StockNewsData):
    """Benzinga Stock News data."""

    class Config:
        fields = {"date": "created", "text": "body"}

    image: List[BenzingaImage] = Field(
        description="The images associated with the news."
    )

    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%a, %d %b %Y %H:%M:%S %z")


class BenzingaStockNewsFetcher(
    Fetcher[
        BenzingaStockNewsQueryParams,
        BenzingaStockNewsData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BenzingaStockNewsQueryParams:
        return BenzingaStockNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BenzingaStockNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[BenzingaStockNewsData]:
        api_key = credentials.get("benzinga_api_key") if credentials else ""

        base_url = "https://api.benzinga.com/api/v2/news"
        querystring = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{querystring}&token={api_key}"
        data = get_data(request_url, **kwargs)

        if len(data) == 0:
            raise RuntimeError("No news found")

        return [BenzingaStockNewsData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[BenzingaStockNewsData],
    ) -> List[BenzingaStockNewsData]:
        # {"image": lambda x: "" if x == [] else x[0].url}
        return data