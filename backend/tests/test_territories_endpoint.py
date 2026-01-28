import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_territory_endpoints():
    """Test territory endpoints verify data structure and handling of new sources."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test Stats
        response = await client.get("/api/territories/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "total_territories" in stats
        assert "by_source" in stats
        # Verify new sources exist in stats
        assert "tjenestetorget" in stats["by_source"]
        assert "eiendomsmegler" in stats["by_source"]
        assert "meglersmart" in stats["by_source"]

        # 2. Test List
        response = await client.get("/api/territories?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        if data["items"]:
            item = data["items"][0]
            assert "office" in item
            assert "postal_info" in item
            assert "source" in item
            assert "source_display_name" in item

        # 3. Test Layers
        response = await client.get("/api/territories/layers")
        assert response.status_code == 200
        layers = response.json()
        assert "layers" in layers
        assert isinstance(layers["layers"], list)
