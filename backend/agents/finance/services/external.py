import httpx
import logging
import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
from core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import resend

logger = logging.getLogger(__name__)

if settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY

class ExternalAPIService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.redis_cache = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.CACHE_TTL = 1800 # 30 minutes

    async def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        cached = await self.redis_cache.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def _set_cached(self, key: str, data: Dict[str, Any], ttl: int = None):
        await self.redis_cache.set(key, json.dumps(data), ex=ttl or self.CACHE_TTL)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _make_request(self, url: str, params: Dict = None) -> Dict[str, Any]:
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch weather data from OpenWeather."""
        cache_key = f"weather_{lat}_{lon}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"lat": lat, "lon": lon, "appid": settings.WEATHER_API_KEY, "units": "metric"}
            data = await self._make_request(url, params)
            await self._set_cached(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"OpenWeather API failed: {e}")
            return {"status": "Clear", "temperature_celsius": 22, "fallback": True}

    async def get_route(self, origin: list, destination: list) -> Dict[str, Any]:
        """Fetch route data from Google Maps Directions API. coordinates format: [lon, lat]"""
        cache_key = f"route_{origin[0]}_{origin[1]}_{destination[0]}_{destination[1]}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            # Google Maps uses lat,lng format
            params = {
                "origin": f"{origin[1]},{origin[0]}",
                "destination": f"{destination[1]},{destination[0]}",
                "key": settings.GOOGLE_MAPS_API_KEY
            }
            data = await self._make_request(url, params)
            
            # Parse Google Maps response to match expected format roughly
            if data.get("status") == "OK" and data.get("routes"):
                leg = data["routes"][0]["legs"][0]
                distance_km = leg["distance"]["value"] / 1000.0
                duration_hours = leg["duration"]["value"] / 3600.0
                parsed_data = {"distance_km": distance_km, "duration_hours": duration_hours, "fallback": False}
                await self._set_cached(cache_key, parsed_data)
                return parsed_data
            else:
                logger.error(f"Google Maps API failed with status: {data.get('status')}")
                return {"distance_km": 150, "duration_hours": 2.5, "fallback": True}
        except Exception as e:
            logger.error(f"Google Maps API request failed: {e}")
            return {"distance_km": 150, "duration_hours": 2.5, "fallback": True}

    async def get_news(self, query: str) -> Dict[str, Any]:
        """Fetch news from NewsAPI."""
        cache_key = f"news_{query}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        try:
            url = "https://newsapi.org/v2/everything"
            params = {"q": query, "apiKey": settings.NEWS_API_KEY, "pageSize": 5}
            data = await self._make_request(url, params)
            await self._set_cached(cache_key, data, ttl=3600) # cache for 1 hr
            return data
        except Exception as e:
            logger.error(f"NewsAPI failed: {e}")
            return {"query": query, "articles": [], "fallback": True}

    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        cache_key = f"exchange_{base_currency}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        try:
            url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/latest/{base_currency}"
            data = await self._make_request(url)
            await self._set_cached(cache_key, data, ttl=86400) # cache for 24h
            return data
        except Exception as e:
            logger.error(f"ExchangeRate API failed: {e}")
            return {"base": base_currency, "rates": {"EUR": 0.92}, "fallback": True}

    async def get_holidays(self, year: int, country_code: str) -> Dict[str, Any]:
        """Fetch holidays from Nager.Date (No API Key)"""
        cache_key = f"holidays_{year}_{country_code}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
            data = await self._make_request(url)
            await self._set_cached(cache_key, {"holidays": data}, ttl=86400)
            return {"holidays": data}
        except Exception as e:
            logger.error(f"Nager.Date API failed: {e}")
            return {"holidays": [], "fallback": True}

    async def get_time(self, timezone: str) -> Dict[str, Any]:
        """Fetch time from WorldTimeAPI (No API Key)"""
        try:
            url = f"http://worldtimeapi.org/api/timezone/{timezone}"
            return await self._make_request(url)
        except Exception as e:
            logger.error(f"WorldTimeAPI failed: {e}")
            return {"fallback": True}

    async def get_country_info(self, country_name: str) -> Dict[str, Any]:
        """Fetch info from REST Countries API (No API Key)"""
        cache_key = f"country_{country_name}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        try:
            url = f"https://restcountries.com/v3.1/name/{country_name}"
            data = await self._make_request(url)
            await self._set_cached(cache_key, {"data": data}, ttl=86400*7) # 1 week cache
            return {"data": data}
        except Exception as e:
            logger.error(f"REST Countries API failed: {e}")
            return {"fallback": True}

    async def geocode(self, address: str) -> Dict[str, Any]:
        """Geocode using OpenStreetMap Nominatim (No API Key)"""
        cache_key = f"geocode_{address}"
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": address, "format": "json"}
            # Nominatim requires a custom User-Agent
            headers = {"User-Agent": "ABCC_SupplyChainAgent/1.0"}
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            await self._set_cached(cache_key, {"data": data})
            return {"data": data}
        except Exception as e:
            logger.error(f"Nominatim API failed: {e}")
            return {"fallback": True}

    async def send_email_alert(self, to_email: str, subject: str, html_content: str):
        """Send email alert using Resend."""
        if not settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY missing. Cannot send email alert.")
            return False
            
        try:
            r = resend.Emails.send({
                "from": "abcc@resend.dev", # Resend allows sending from this domain on free tier if verified
                "to": to_email,
                "subject": subject,
                "html": html_content
            })
            return r
        except Exception as e:
            logger.error(f"Resend API failed: {e}")
            return False

external_api_service = ExternalAPIService()
