"use client";

import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import type { FeatureCollection, Feature, Geometry } from "geojson";
import type { TerritoryMapData } from "@/types/v3";
import "leaflet/dist/leaflet.css";
import * as L from "leaflet";
// Use the dist path if resolution fails in some environments
// import * as L from "leaflet/dist/leaflet-src.js";


// Fix for default marker icons in Leaflet with Next.js
const fixLeafletIcons = () => {
  // @ts-expect-error - Leaflet types are a bit tricky here
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });
};

interface TerritoryMapProps {
  mapData: TerritoryMapData;
  geometryData: Record<string, Feature | Geometry>;
}

function MapUpdater({ features }: { features: Feature[] }) {
  const map = useMap();

  useEffect(() => {
    if (features && features.length > 0) {
      const bounds = L.latLngBounds([]);
      features.forEach((f) => {
        if (f.geometry) {
            try {
                const layer = L.geoJSON(f);
                bounds.extend(layer.getBounds());
            } catch {
                // Ignore invalid geometries
            }
        }
      });
      
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] });
      } else {
        map.setView([65, 13], 4);
      }
    }
  }, [features, map]);

  return null;
}

export default function TerritoryMap({ mapData, geometryData }: TerritoryMapProps) {
  useEffect(() => {
    fixLeafletIcons();
  }, []);

  const geoJsonData = useMemo(() => {
    if (!mapData || !geometryData) return null;

    const features: Feature[] = [];

    mapData.features.forEach((feature) => {
      const pc = feature.properties.postal_code;
      const geometryEntry = geometryData[pc];

      if (geometryEntry) {
        // The shared geometry file contains full Feature objects
        const actualGeometry = geometryEntry.type === "Feature" 
          ? geometryEntry.geometry 
          : geometryEntry;
        
        features.push({
          type: "Feature",
          properties: feature.properties,
          geometry: actualGeometry,
        });
      }

    });

    return {
      type: "FeatureCollection",
      features: features,
    } as FeatureCollection;
  }, [mapData, geometryData]);

  const onEachFeature = (feature: Feature, layer: L.Layer) => {
    if (feature.properties) {
      const { postal_code, postal_name, office_name, source } = feature.properties;
      layer.bindPopup(`
        <div class="p-1">
          <div class="font-bold">${postal_code} ${postal_name}</div>
          <div class="text-xs text-muted-foreground mb-1">${source}</div>
          <div class="text-sm border-t pt-1 mt-1">
            Tildelt: <span class="font-semibold">${office_name || "Ukjent"}</span>
          </div>
        </div>
      `);
    }
  };

  const geoJsonStyle = (feature?: Feature) => {
    const isBlacklisted = feature?.properties?.is_blacklisted;
    const color = feature?.properties?.office_color || "#272630";

    return {
      fillColor: isBlacklisted ? "#666666" : color,
      weight: 1,
      opacity: 1,
      color: "white",
      fillOpacity: isBlacklisted ? 0.3 : 0.6,
    };
  };

  return (
    <div className="h-[500px] w-full rounded-lg overflow-hidden border border-[#E5E5E5] relative">
      <MapContainer
        center={[65, 13]}
        zoom={4}
        scrollWheelZoom={true}
        className="h-full w-full z-10"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {geoJsonData && (
          <>
            <GeoJSON
              data={geoJsonData}
              style={geoJsonStyle}
              onEachFeature={onEachFeature}
            />
            <MapUpdater features={geoJsonData.features} />
          </>
        )}
      </MapContainer>
    </div>
  );
}
